" 项目: gvim 配置文件 
" 安装: sudo apt-get install vim-gtk 
" 用法: 将本文件(.vimrc)拷贝到$HOME/ 

" 使用 murphy 调色板 
 colo desert
" 设置用于GUI图形用户界面的字体列表。 
"set guifont=BitStream\ Vera\ Sans\ Mono\ 10 
" 
set nocompatible 
" 设定文件浏览器目录为当前目录 
set bsdir=buffer 
set autochdir 
" 设置编码 
set enc=utf-8 
" 设置文件编码 
set fenc=utf-8 
" 设置文件编码检测类型及支持格式 
set fencs=utf-8,ucs-bom,gb18030,gbk,gb2312,cp936 
" 指定菜单语言 
set langmenu=zh_CN.UTF-8 
source $VIMRUNTIME/delmenu.vim 
source $VIMRUNTIME/menu.vim 
" 设置语法高亮度 
"set syn
syntax on
"显示行号 
set nu! 
set paste
" 查找结果高亮度显示 
set hlsearch 
" tab宽度 
set tabstop=4 
set cindent shiftwidth=4 
"set autoindent shiftwidth=4
set noai
" C/C++注释 
set comments=:// 
" 修正自动C式样注释功能 <2005/07/16> 
set comments=s1:/*,mb:*,ex0:/ 
" 增强检索功能 
set tags=./tags,./../tags,./**/tags 
" 保存文件格式 
set fileformats=unix,dos 
" 键盘操作 
map <Up> gk 
map <Down> gj 
" 命令行高度 
set cmdheight=1 
" 中文帮助 
if version > 603 
set helplang=cn 
endi 
command! -bar -nargs=0 SudoW   :silent exe "write !sudo tee % >/dev/null"|silent edit!
