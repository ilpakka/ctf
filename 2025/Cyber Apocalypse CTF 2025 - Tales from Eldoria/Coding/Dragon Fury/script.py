import ast

input_text = input()
target_damage = int(input())

damage_values = ast.literal_eval(input_text)

def find_combination(damage_values, target_damage):
    def helper(index, current_combination, current_sum):
        if index == len(damage_values):
            if current_sum == target_damage:
                return current_combination
            else:
                return None
        
        for value in damage_values[index]:
            result = helper(index + 1, current_combination + [value], current_sum + value)
            if result:
                return result  
        return None
    return helper(0, [], 0)

valid_combination = find_combination(damage_values, target_damage)

print(valid_combination)
