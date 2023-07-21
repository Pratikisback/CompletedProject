num = int(input("Enter the number: ")) # 321
n = num
reverse = 0
if n > 0:
    while n != 0:
        reminder = n % 10
        reverse = reverse * 10 + reminder
        n = n // 10
    print(reverse)