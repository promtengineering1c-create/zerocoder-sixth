def main():
    # grid = [[1,4],[2,3]]
    # grid = [[28443],[33959]]
    # grid = [[54756,54756]]
    grid = [[9753,4621,3652],[3003,4050,433]]


    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    print(rows, cols)
    print(range(rows))
    print(range(cols))    

    done = False
    if rows > 1:
        rows_grid = [0] * rows
        for r in range(rows+1):
            rows_grid[r-1] = sum(grid[r-1]) 
        up = 0;   
        down = sum(rows_grid) 

        for i in range(len(rows_grid)):
            up += rows_grid[i]
            down -= rows_grid[i]     
            if up == down:
                done = True
                print(f"Строк: {i + 1}, результат: {up}")
                return done            

    if not done:
        if cols > 1 and rows > 1:
            new_grid = [[0] * rows for _ in range(cols)]

            for r in range(rows+1):
                for c in range(cols+1):
                    new_grid[c-1][r-1] = grid[r-1][c-1]

            cols_grid = [0] * cols
            for c in range(cols+1):
                cols_grid[c-1] = sum(new_grid[c-1]) 

            right = 0;   
            Left = sum(cols_grid) 

            done = False
            for i in range(len(cols_grid)):
                right += cols_grid[i]
                Left -= cols_grid[i] 
                if right == Left:
                    done = True
                    print(f"Колонок: {i + 1}, результат: {right}")
                    return done
        elif cols > 0:  
            new_grid = grid[0]      
            cols_grid = [0] * len(new_grid)
            for r in range(len(new_grid)+1):
                cols_grid[r-1] = new_grid[r-1] 

            right = 0;   
            Left = sum(cols_grid) 
            done = False
            for i in range(len(cols_grid)):
                right += cols_grid[i]
                print(right)
                Left -= cols_grid[i] 
                print(Left)
                if right == Left:
                    done = True
                    print(f"Колонок: {i + 1}, результат: {right}")
                    return done
    # print(new_grid)

result = main()
print(result)