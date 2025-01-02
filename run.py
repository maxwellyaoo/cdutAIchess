import subprocess
def run_command(choice):
    if choice == '1':
        command = 'python .\MaoHouPao\main.py'  # 根据输入1运行 main.py进行命令行人机对弈
    elif choice == '2':
        command = 'python -m MyChess.Chess_UI.win_game'  # 根据输入2运行 MyChess.Chess_UI.win_game进行图形界面双人对弈
    else:
        print("无效的选择。")
        return
    # 执行命令
    try:
        subprocess.run(command, shell=True, check=True)  # 使用shell=True允许传递命令字符串
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
def main():
    user_input = input("请输入 '1' 进行人机对弈，输入 '2' 执行 双人对弈：\n——")
    run_command(user_input)
if __name__ == "__main__":
    main()
