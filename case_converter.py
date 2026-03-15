def to_uppercase(text):
    """将文本转换为大写"""
    return text.upper()


def to_lowercase(text):
    """将文本转换为小写"""
    return text.lower()


def to_capitalize(text):
    """将文本首字母大写"""
    return text.capitalize()


def show_menu():
    """显示菜单选项"""
    print("\n" + "=" * 40)
    print("       单词大小写转换工具")
    print("=" * 40)
    print("1. 全部大写 (UPPERCASE)")
    print("2. 全部小写 (lowercase)")
    print("3. 首字母大写 (Capitalize)")
    print("0. 退出程序")
    print("=" * 40)


def get_user_choice():
    """获取用户选择的转换类型"""
    while True:
        choice = input("请选择转换类型 (0-3): ").strip()
        if choice in ['0', '1', '2', '3']:
            return choice
        print("无效的选择，请输入 0-3 之间的数字。")


def main():
    """主程序"""
    print("欢迎使用单词大小写转换工具！")

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == '0':
            print("\n感谢使用，再见！")
            break

        # 获取用户输入的文本
        user_input = input("\n请输入要转换的英文单词/句子: ").strip()

        if not user_input:
            print("输入不能为空，请重新输入。")
            continue

        # 根据选择执行相应的转换
        if choice == '1':
            result = to_uppercase(user_input)
            print(f"\n【全部大写】转换结果:")
        elif choice == '2':
            result = to_lowercase(user_input)
            print(f"\n【全部小写】转换结果:")
        elif choice == '3':
            result = to_capitalize(user_input)
            print(f"\n【首字母大写】转换结果:")

        print(f">>> {result}")

        # 询问是否继续
        continue_choice = input("\n是否继续转换? (y/n): ").strip().lower()
        if continue_choice != 'y':
            print("\n感谢使用，再见！")
            break


if __name__ == "__main__":
    main()
