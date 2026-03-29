print("=" * 40)
print("    单词大小写转换工具")
print("=" * 40)

while True:
    print("\n请输入要转换的英文单词或句子:")
    user_input = input("> ")

    print("\n请选择转换类型:")
    print("1. 全部大写")
    print("2. 全部小写")
    print("3. 首字母大写")

    choice = input("\n请输入选项 (1/2/3): ")

    if choice == '1':
        result = user_input.upper()
        print(f"\n转换结果: {result}")
    elif choice == '2':
        result = user_input.lower()
        print(f"\n转换结果: {result}")
    elif choice == '3':
        result = user_input.capitalize()
        print(f"\n转换结果: {result}")
    else:
        print("\n无效的选项，请重新选择!")
        continue

    again = input("\n是否继续转换? (y/n): ")
    if again.lower() != 'y':
        print("\n感谢使用大小写转换工具，再见!")
        break
