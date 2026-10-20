
import ast 
import operator

binary_operatons = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
unary_operatoions = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def _eval(node, names):
    if isinstance(node, ast.Expression):
        return _eval(node.body, names)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in binary_operatons:
        return binary_operatons[type(node.op)](_eval(node.left, names), _eval(node.right, names))
    if isinstance(node, ast.UnaryOp) and type(node.op) in unary_operatoions:
        return unary_operatoions[type(node.op)](_eval(node.operand, names))
    raise ValueError("unsupported expression")

def calculate(text, ans=0):

    tree = ast.parse(text.strip(), mode="eval")
    return _eval(tree, {"ans": ans})
 


def main():
    ans = 0
    while True:
        try:
            line = input("> ").strip()
        except:
            print()
            break 
        if not line:
            continue
        if line.lower() in ("q", "quit", "exit" "byebye"):
            break 

        try:
            ans = calculate(line, ans)
            print(ans)
        except:
            print("an error occured, maybe don't type numbers or divide by zero")

if __name__ == "__main__":
    main()

