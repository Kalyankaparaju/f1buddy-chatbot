from yelp_api import search_places

def greet():
    print("👋 Welcome to F1Buddy – your local guide for budget restaurants and groceries!")
    print("Type 'exit' anytime to quit.\n")

def main():
    greet()
    while True:
        city = input("📍 Enter your city (e.g., Fremont, CA): ")
        if city.lower() == 'exit':
            break
        category = input("🍽️  Type 'restaurant' or 'grocery': ")
        if category.lower() == 'exit':
            break

        term = "cheap " + ("restaurants" if category == "restaurant" else "grocery stores")
        results = search_places(term=term, location=city)

        if not results:
            print("❌ No results found. Try a different city.\n")
            continue

        print(f"\nTop {category}s in {city}:")
        for biz in results:
            name = biz.get("name")
            addr = ", ".join(biz['location'].get('display_address', []))
            price = biz.get("price", "?")
            print(f" - {name} | {price} | {addr}")
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
