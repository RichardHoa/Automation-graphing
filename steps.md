1. Access the main.py
<!-- 1.Store all the `from import` statements -->
2. Go through all the functions, a function is defined with () at the end, store all of this functions in a list
3. Visit each function one by one:
   - If that function exists on the file:
     look into it. move to ------Look into the function------
   - Else:
     Look to the file who has the function by looking at the reference `from import`. Move to ------Look into the function------
     - If found no such reference => it's a library functions, skip this

------Look into the function------

- If the inside functions has the same name as the outside functions, it's a recursive functions and should be stop there. Add this function to the function_order list

1. Repeat step 2
2. Repeat step 3
3. Draw the function, the function before will point to the function after
4. return True to exist the function

Things to find out:

- library to draw the canvas and arrow easy

{
'A':
{'B':{'C': {
"D": {}
}},
'F': {'G': {}}
}
}
