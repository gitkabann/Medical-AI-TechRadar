from app.tools.chroma_client import collection

results = collection.get(include=["documents", "metadatas"])

for i in range(len(results["ids"])):
    print("\n================ Chroma Chunk ================")
    print("ID:", results["ids"][i])
    print("Content:", results["documents"][i])
    print("Metadata:", results["metadatas"][i])
