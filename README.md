# Tools（一些工具类脚本，部分在Unix Like系统有对应bash脚本）

1.prename.py: 批量重命名文件
2.search_same_file.py: 搜索具有相同内容的文件
3.source_code_process.py: 从源文件里提取不同内容（注释、字符串、源码）
4.unused_resource.py: 检索工程中未使用的资源文件，注意没有区分一些asset的使用场景，所以结果不是很准确
5.unused_selectors.py: 通过可执行文件和link map文件，分析不曾使用的一些方法，需要二次确认，一些系统调用和property可能会误报
6.utilities.py: 为其他脚本服务的通用函数
