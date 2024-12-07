import redis
from mongoengine import *
from models import Quote, Author
import pickle


redis_client = redis.StrictRedis(host="localhost", port=6379)

def cache_result(key, result):
    redis_client.set(key, pickle.dumps(result), ex=3600)

def get_cached_result(key):
    cached_data = redis_client.get(key)
    if cached_data:
        return pickle.loads(cached_data)
    return None

def search():
    while True:
        command = input("Enter the command (eg name:Steve Martin): ").strip()

        if command.lower() == "exit":
            print("Completion of work.")
            break

        try:
            key, value = command.split(":")
        except ValueError:
            print("Invalid command format. Try again.")
            continue

        if key == "name" and len(value) == 2:
            value = value.capitalize()
        elif key == "tag" and len(value) == 2:
            value = value.lower()

        cache_key = f"{key}:{value}"
        cached_result = get_cached_result(cache_key)
        if cached_result:
            print("Result from the cache:")
            for quote, author in cached_result:
                print(f"{author}: {quote}".encode("utf-8").decode("utf-8"))
            continue

        if key == "name":
            author = Author.objects(fullname__icontains=value.strip()).first()
            if author:
                author_quotes = Quote.objects(author=author)
                if author_quotes:
                    quotes_list = [(quote.quote, author.fullname) for quote in author_quotes]
                    cache_result(cache_key, quotes_list)
                    for quote, author_name in quotes_list:
                        print(f"{author_name}: {quote}".encode("utf-8").decode("utf-8"))
                else:
                    print("No quotes found for this author.")
            else:
                print(f"Author '{value}' not found.")

        elif key == "tag":
            tag_quotes = Quote.objects(tags__in=[value.strip()])
            if tag_quotes:
                quotes_list = [(quote.quote, quote.author.fullname) for quote in tag_quotes]
                cache_result(cache_key, quotes_list)
                for quote, author in quotes_list:
                    print(f"{author}: {quote}".encode("utf-8").decode("utf-8"))
            else:
                print("No quotes with this tag were found.")

        elif key == "tags":
            tags = [tag.strip() for tag in value.split(",")]
            tag_quotes = Quote.objects(tags__in=tags)
            if tag_quotes:
                quotes_list = [(quote.quote, quote.author.fullname) for quote in tag_quotes]
                cache_result(cache_key, quotes_list)
                for quote, author in quotes_list:
                    print(f"{author}: {quote}".encode("utf-8").decode("utf-8"))
            else:
                print("No quotes found with these tags.")

        else:
            print("Unknown command. Try again.")


if __name__ == '__main__':
    search()