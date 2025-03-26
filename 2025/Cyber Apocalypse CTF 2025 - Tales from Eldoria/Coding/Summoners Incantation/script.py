input_text = input()

def max_energy(tokens):
    if not tokens:
        return 0
    
    include = 0
    exclude = 0
    
    for token in tokens:
        new_include = exclude + token
        new_exclude = max(include, exclude)
        include, exclude = new_include, new_exclude

    return max(include, exclude)


try:
    tokens = eval(input_text)
    if isinstance(tokens, list):
        result = max_energy(tokens)
        print(result)
    else:
        print("list not int")
except Exception as e:
    print(f"{e}")