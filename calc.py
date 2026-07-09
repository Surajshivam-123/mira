import streamlit as st

def add(num1: str, num2: str) -> str:
    i = len(num1) - 1
    j = len(num2) - 1
    carry = 0
    res = []

    while i >= 0 or j >= 0 or carry:
        d1 = int(num1[i]) if i >= 0 else 0
        d2 = int(num2[j]) if j >= 0 else 0
        total = d1 + d2 + carry
        res.append(str(total % 10))
        carry = total // 10
        i -= 1
        j -= 1

    return ''.join(reversed(res))

def sub(num1: str, num2: str) -> str:
    negative = False
    if len(num1) < len(num2) or (len(num1) == len(num2) and num1 < num2):
        num1, num2 = num2, num1
        negative = True
    i = len(num1) - 1
    j = len(num2) - 1
    borrow = 0
    res = []
    while i >= 0:
        d1 = int(num1[i])
        d2 = int(num2[j]) if j >= 0 else 0

        total = d1 - d2 - borrow

        if total < 0:
            total += 10
            borrow = 1
        else:
            borrow = 0

        res.append(str(total))

        i -= 1
        j -= 1

    while len(res) > 1 and res[-1] == '0':
        res.pop()

    ans = ''.join(reversed(res))
    return "-" + ans if negative else ans

def multiply(num1: str, num2: str) -> str:
    if num1 == "0" or num2 == "0":
        return "0"

    n, m = len(num1), len(num2)
    res = [0] * (n + m)

    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            mul = int(num1[i]) * int(num2[j])

            p1 = i + j
            p2 = i + j + 1

            total = mul + res[p2]

            res[p2] = total % 10
            res[p1] += total // 10

    i = 0
    while i < len(res) - 1 and res[i] == 0:
        i += 1
    return ''.join(map(str, res[i:]))

def divide(dividend: str, divisor: str) -> str:
    if divisor == "0":
        raise ValueError("Division by zero")

    if dividend == "0":
        return "0"
    def smaller(a, b):
        if len(a) != len(b):
            return len(a) < len(b)
        return a < b
    def subtract(a, b):
        i, j = len(a)-1, len(b)-1
        borrow = 0
        ans = []

        while i >= 0:
            x = int(a[i])
            y = int(b[j]) if j >= 0 else 0

            x -= borrow

            if x < y:
                x += 10
                borrow = 1
            else:
                borrow = 0

            ans.append(str(x-y))
            i -= 1
            j -= 1

        while len(ans) > 1 and ans[-1] == '0':
            ans.pop()

        return ''.join(reversed(ans))

    quotient = ""
    current = ""

    for ch in dividend:
        current += ch
        current = current.lstrip('0') or "0"

        digit = 0
        while not smaller(current, divisor):
            current = subtract(current, divisor)
            digit += 1

        quotient += str(digit)

    quotient = quotient.lstrip('0')
    return quotient if quotient else "0"


st.set_page_config(
    page_title="Large Number Calculator",
    page_icon="🧮",
    layout="centered"
)
num1=st.text_input("Enter 1st number: ")
num2=st.text_input("Enter 2nd number: ")

col1, col2, col3, col4 = st.columns(4)

result = None

with col1:
    if st.button("➕"):
        result = add(num1, num2)
with col2:
    if st.button("➖"):
        result = sub(num1, num2)

with col3:
    if st.button("✖"):
        result = multiply(num1, num2)

with col4:
    if st.button("➗"):
        result = divide(num1, num2)

if(result):
    st.write(result)
else:
    st.write("Invalid Number !")