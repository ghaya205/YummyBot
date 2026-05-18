import os
import json
import base64
from dotenv import load_dotenv
from groq import Groq

# LOAD API KEY
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
api_key = os.getenv("GROQ_API_KEY")
print(f"✅ API Key loaded: {api_key[:10]}...")

# LOAD DATASET
with open(os.path.join(os.path.dirname(__file__), '..', 'Data', 'tunisian_recipes.json'), encoding="utf-8") as f:
    recipes = json.load(f)
print(f"✅ Loaded {len(recipes)} recipes")

# ─────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────
client = Groq(api_key=api_key)

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# ─────────────────────────────────────────
# TOOL FUNCTIONS
# ─────────────────────────────────────────
def RecipeSearch(query: str) -> str:
    query = query.lower()
    results = [
        r for r in recipes
        if query in str(r.get("name", "")).lower()
        or query in str(r.get("ingredients", "")).lower()
    ]
    if results:
        top3 = results[:3]
        output = f"Found {len(results)} recipes. Top 3:\n"
        for r in top3:
            output += f"\n🍽️ {r.get('name')}\n"
            output += f"   Ingredients: {r.get('ingredients')}\n"
            output += f"   Steps: {r.get('steps')}\n"
            output += f"   Cook time: {r.get('cook_time')}\n---"
        return output
    return f"No recipe found for: {query}"

def WebSearch(query: str) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query + " recipe", max_results=3))
        if results:
            output = "Web results:\n"
            for r in results:
                output += f"\n🌐 {r['title']}\n{r['body']}\n---"
            return output
        return "No web results found."
    except Exception as e:
        return f"Web search failed: {str(e)}"

def IngredientSubstitute(ingredient: str) -> str:
    substitutes = {
        "harissa": "chili paste or sriracha",
        "merguez": "spicy lamb sausage",
        "tabil": "coriander + caraway mix",
        "preserved lemon": "fresh lemon zest",
        "smen": "aged butter or ghee",
        "frik": "bulgur wheat or freekeh",
        "malsouka": "filo pastry sheets",
        "brik pastry": "filo pastry sheets",
        "ras el hanout": "cumin + coriander + cinnamon + ginger",
        "orange blossom water": "rose water or vanilla extract"
    }
    result = substitutes.get(ingredient.lower().strip())
    if result:
        return f"✅ Substitute for '{ingredient}': {result}"
    return f"No substitute found for '{ingredient}'. Try WebSearch!"

# ─────────────────────────────────────────
# TOOLS DEFINITION
# ─────────────────────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "RecipeSearch",
            "description": "Search for food recipes in the local database. Use this first for any recipe request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term, e.g. 'Brik', 'chicken', 'tuna'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "WebSearch",
            "description": "Search the web for recipes or cooking tips not found in the local database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "IngredientSubstitute",
            "description": "Get a substitute for a missing or unavailable ingredient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ingredient": {
                        "type": "string",
                        "description": "The ingredient name to find a substitute for"
                    }
                },
                "required": ["ingredient"]
            }
        }
    }
]

# ─────────────────────────────────────────
# TOOL DISPATCHER
# ─────────────────────────────────────────
def run_tool(name, args):
    if name == "RecipeSearch":
        return RecipeSearch(args.get("query", ""))
    elif name == "WebSearch":
        return WebSearch(args.get("query", ""))
    elif name == "IngredientSubstitute":
        return IngredientSubstitute(args.get("ingredient", ""))
    return f"Unknown tool: {name}"

# ─────────────────────────────────────────
# MEMORY
# ─────────────────────────────────────────
chat_history = [
    {
        "role": "system",
        "content": (
            "You are a helpful food recipe assistant specializing in Tunisian and international cuisine.\n"
            "- Always call RecipeSearch first when the user asks about a recipe.\n"
            "- Call IngredientSubstitute when the user asks for a substitute.\n"
            "- Call WebSearch only if RecipeSearch returns no results.\n"
            "- Never answer recipe questions from memory alone; always use your tools first.\n"
            "- Be friendly, detailed, and format recipes clearly with ingredients and steps."
        )
    }
]

# ─────────────────────────────────────────
# CHAT FUNCTION
# ─────────────────────────────────────────
def chat(user_input):
    chat_history.append({"role": "user", "content": user_input})

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=chat_history,
                tools=tools,
                tool_choice="auto",
                max_tokens=1024
            )
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            chat_history.append({"role": "assistant", "content": error_msg})
            return error_msg

        message = response.choices[0].message

        if not message.tool_calls:
            reply = message.content or "Sorry, I couldn't generate a response."
            chat_history.append({"role": "assistant", "content": reply})
            return reply

        chat_history.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}

            try:
                tool_result = run_tool(tc.function.name, args)
            except Exception as e:
                tool_result = f"Tool '{tc.function.name}' failed: {str(e)}"

            chat_history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(tool_result)
            })

    fallback = "I'm sorry, I couldn't complete the request. Please try again."
    chat_history.append({"role": "assistant", "content": fallback})
    return fallback

# ─────────────────────────────────────────
# IMAGE IDENTIFICATION FUNCTION
# ─────────────────────────────────────────
def identify_dish_from_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = image_path.split(".")[-1].lower()
    if ext in ["jpg", "jpeg"]:
        mime = "image/jpeg"
    elif ext == "png":
        mime = "image/png"
    elif ext == "webp":
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": (
                            "Look at this food image carefully.\n"
                            "1. Identify the dish name\n"
                            "2. List the main ingredients you can see\n"
                            "3. Guess the cuisine (Tunisian, Italian, French, etc.)\n\n"
                            "Respond in this exact format:\n"
                            "Dish: [name]\n"
                            "Ingredients: [list]\n"
                            "Cuisine: [type]"
                        )
                    }
                ]
            }
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()


def chat_with_image(image_path: str) -> str:
    print(f"🔍 Analyzing image: {image_path}")

    try:
        identification = identify_dish_from_image(image_path)
    except Exception as e:
        return f"❌ Could not analyze the image: {str(e)}"

    print(f"✅ Vision result:\n{identification}")

    dish_name = "this dish"
    for line in identification.split("\n"):
        if line.startswith("Dish:"):
            dish_name = line.replace("Dish:", "").strip()
            break

    recipe_result = chat(f"Give me the full detailed recipe for {dish_name} with ingredients and steps")

    return f"""## 🔍 Image Analysis
{identification}

---

## 📖 Recipe for {dish_name}
{recipe_result}"""


# ─────────────────────────────────────────
# TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n--- Test 1 ---")
    print(chat("How do I make Brik?"))
    print("\n--- Test 2 ---")
    print(chat("I don't have harissa, what can I use?"))
    print("\n--- Test 3 (memory) ---")
    print(chat("What was my first question?"))
