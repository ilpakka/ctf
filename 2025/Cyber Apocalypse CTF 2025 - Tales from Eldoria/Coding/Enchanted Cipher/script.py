input_text = input()


num_groups = int(input())

shift_values = eval(input())

def decode_text(text, shifts):
    words = text.split()
    word_lengths = [len(word) for word in words]
    
    text = text.replace(' ', '')
    decoded_chars = []
    shift_index = 0
    
    for i in range(0, len(text), 5):
        group = text[i:i + 5]
        
        if shift_index < len(shifts):
            shift = shifts[shift_index]
            for char in group:
                decoded = chr(((ord(char.lower()) - ord('a') - shift) % 26) + ord('a'))
                decoded_chars.append(decoded)
            
            shift_index += 1
    
    result = []
    pos = 0
    for length in word_lengths:
        word = ''.join(decoded_chars[pos:pos + length])
        result.append(word)
        pos += length
    return ' '.join(result)

decoded_text = decode_text(input_text, shift_values)

print(decoded_text)
