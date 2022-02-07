files = {
    ("aaa", "bbb", "ccc"): "whatever shiut here",
    ("ddd", "eee", "fff", "ggg", "hhh"): "some test content hehe",
    ("jkah", "asd", "ojah", "iujah", "89ajs"): "some other contens sghut gere loal",
    ("kjahsd", "28793h", "kjhsd", "8127J", "JKAHSDKJAHDSJK", "jaunmsmn", "a"): "whavteer",
    ("jha", "uimn30"): "kjasdjkhaskjdhakjhsdkjhsj"
}

for names, content in files.items():
    for name in names:
        with open(f"files/{name}.txt", "w") as f:
            f.write(content)
