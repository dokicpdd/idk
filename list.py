def create_tasks():
    tasks=set()
    while True:
        print()
        print('enter 1 for adding a new task')
        print('enter 2 for deleting a new task')
        print('enter 3 for displaying the task list')
        print('enter 4 for quiting the program and get ur tasks\n')

        number=int(input('which one do u choose'))
        print()
        match number:
            case 1:
                task=input('type in the task name\n')
                tasks.add(task)
            case 2:
                task=input('type in the task u want to remove\n')
                if task in tasks:
                    tasks.remove(task)
            case 3:
                l=len(tasks)
                for task in tasks:
                    print(task)
                print()
            case 4:
                break
            case _:
                break
    return tasks

if __name__=='__main__':
    create_tasks()