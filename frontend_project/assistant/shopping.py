# shopping.py
import webbrowser
from ai import ask_ai

def handle_shopping_query(cmd: str, takecommand, speak, lang="en"):
    """
    Handle shopping/food/movie queries with AI suggestions + follow-up.
    1. If user asks for suggestion → AI suggests items.
    2. Then assistant asks if user wants to order/book.
    3. If user says 'yes' with item → open site with that item.
    4. If user says 'no' → stop.
    """
    cmd = cmd.lower()

    # --- Suggestions ---
    if "suggest" in cmd or "recommend" in cmd:
        # Food
        if "food" in cmd or "dish" in cmd or "south indian" in cmd:
            prompt = "Suggest 3 famous South Indian foods trending right now."
            reply, _ = ask_ai(prompt)
            speak(reply, lang)

            speak("Should I order one of these for you on Zomato?", lang)
            choice = takecommand(lang).lower()
            if "yes" in choice:
                # check if user said food name
                for word in reply.split():
                    if word.lower() in choice:
                        webbrowser.open(f"https://www.zomato.com/search?keyword={word}")
                        return f"Ordering {word} on Zomato."
                webbrowser.open("https://www.zomato.com/")
                return "Opening Zomato for you."
            else:
                return "Okay, I won’t order anything now."

        # Movies
        elif "movie" in cmd or "film" in cmd or "cinema" in cmd:
            prompt = "Suggest 3 trending movies right now."
            reply, _ = ask_ai(prompt)
            speak(reply, lang)

            speak("Should I book tickets for one of these on BookMyShow?", lang)
            choice = takecommand(lang).lower()
            if "yes" in choice:
                for word in reply.split():
                    if word.lower() in choice:
                        webbrowser.open("https://in.bookmyshow.com/")  # direct movie booking not possible
                        return f"Booking tickets for {word} on BookMyShow."
                webbrowser.open("https://in.bookmyshow.com/")
                return "Opening BookMyShow for you."
            else:
                return "Okay, no tickets booked."

        # Dresses
        elif "dress" in cmd or "clothes" in cmd or "fashion" in cmd:
            prompt = "Suggest 3 trending dresses or fashion items right now."
            reply, _ = ask_ai(prompt)
            speak(reply, lang)

            speak("Should I open Flipkart to shop for one of these?", lang)
            choice = takecommand(lang).lower()
            if "yes" in choice:
                for word in reply.split():
                    if word.lower() in choice:
                        webbrowser.open(f"https://www.flipkart.com/search?q={word}")
                        return f"Searching {word} on Flipkart."
                webbrowser.open("https://www.flipkart.com/")
                return "Opening Flipkart for you."
            else:
                return "Okay, no shopping done."

        # Not shopping-related (like names, hobbies, etc.)
        else:
            reply, detected_lang = ask_ai(cmd)
            speak(reply, detected_lang)
            return None

    # --- Direct shopping actions ---
    if any(word in cmd for word in ["buy", "shop", "order", "cloth", "dress", "shoes", "mobile", "laptop"]):
        query = cmd.replace("buy", "").replace("shop", "").replace("order", "").strip()
        url = f"https://www.flipkart.com/search?q={query}"
        webbrowser.open(url)
        return f"Here are some results for {query} on Flipkart."

    elif any(word in cmd for word in ["food", "eat", "dinner", "lunch", "breakfast"]):
        query = cmd.replace("food", "").replace("eat", "").strip()
        url = f"https://www.zomato.com/search?keyword={query}"
        webbrowser.open(url)
        return f"Here are some food options for {query} on Zomato."

    elif "pizza" in cmd or "dominos" in cmd:
        url = "https://www.dominos.co.in/menu"
        webbrowser.open(url)
        return "Opening Dominos menu for you."

    elif any(word in cmd for word in ["movie", "ticket", "book show", "cinema"]):
        url = "https://in.bookmyshow.com/"
        webbrowser.open(url)
        return "Opening BookMyShow for tickets."

    return None
