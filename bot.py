import time

def search_news_snippets(query):
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "tbm": "nws",
        "q": query
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=20)
        data = response.json()

        results = data.get("news_results", [])
        if not results:
            return "⚠️ No relevant articles found."

        snippets = []
        for res in results[:3]:
            title = res.get("title", "No title")
            snippet = res.get("snippet", "No summary")
            link = res.get("link", "")
            snippets.append(f"📰 {title}\n{snippet}\n🔗 {link}")

        return "\n\n".join(snippets)

    except requests.exceptions.Timeout:
        # Retry once after short delay
        time.sleep(3)
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=20)
            data = response.json()
            results = data.get("news_results", [])
            if not results:
                return "⚠️ No relevant articles found."

            snippets = []
            for res in results[:3]:
                title = res.get("title", "No title")
                snippet = res.get("snippet", "No summary")
                link = res.get("link", "")
                snippets.append(f"📰 {title}\n{snippet}\n🔗 {link}")

            return "\n\n".join(snippets)

        except Exception as e:
            return f"❌ Search retry failed. Check your internet or API quota. (Error: {e})"

    except Exception as e:
        return f"❌ Could not fetch news from SerpAPI. Please try again later.\n(Error: {e})"
