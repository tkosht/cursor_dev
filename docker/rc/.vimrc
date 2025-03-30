set sw=4 ts=4 sts=4 et
set hlsearch

augroup fileTypeIndent
    autocmd!
    autocmd BufNewFile,BufRead *.py setlocal ts=4 sts=4 sw=4
    autocmd BufNewFile,BufRead *.html setlocal ts=2 sts=2 sw=2
    autocmd BufNewFile,BufRead *.vue setlocal ts=2 sts=2 sw=2
    autocmd BufNewFile,BufRead *.css setlocal ts=2 sts=2 sw=2
augroup END
