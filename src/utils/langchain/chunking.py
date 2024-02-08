from langchain.text_splitter import RecursiveCharacterTextSplitter

text = "This is a test sentence. This is another test sentence. This is a third test sentence."

splitter = RecursiveCharacterTextSplitter()

chunks = splitter.split_text(text)

print(f"{len(chunks)} chunks found.")

for chunk in chunks:
    print(chunk)