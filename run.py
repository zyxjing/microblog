#encoding:utf-8
#!flask/bin/python
'''
能够完整工作的 Web 应用程序的最后一步是创建一个脚本，启动我们的应用程序的开发 Web 服务器。让我们称这个脚本为 run.py，并把它置于根目录:

这个脚本简单地从我们的 app 包中导入 app 变量并且调用它的 run 方法来启动服务器。请记住 app 变量中含有我们在之前创建的 Flask 实例。

要启动应用程序，您只需运行此脚本（run.py）。
在 Windows 上不再需要指明文件是否可执行。相反你必须运行该脚本作为 Python 解释器的一个参数:
'''
from app import app
app.run(debug=False,port = 5000)