from bot import load_database

data = load_database()
print("Database content:", data)
print("Pending images:", data.get("pending_images", "Key not found"))
