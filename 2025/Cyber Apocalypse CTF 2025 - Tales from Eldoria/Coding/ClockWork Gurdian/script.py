from collections import deque


grid_input = input()
grid = eval(grid_input)

def shortest_path(grid):
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    start = (0, 0)
    
    queue = deque([(0, 0, 0)])
    visited = set()
    visited.add(start)
    
    while queue:
        x, y, dist = queue.popleft()
        
        if grid[x][y] == 'E':
            return dist
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                if grid[nx][ny] != 1:
                    visited.add((nx, ny))
                    queue.append((nx, ny, dist + 1))
    return -1

result = shortest_path(grid)

print(result)
