#!/bin/sh

snail1='
@             _________
 \____       /         \
 /    \     /   ____    \  ---
 \_    \   /   /    \    \   ---
   \    \ (    \__/  )    )   ---
    \    \_\ \______/    /   ---
     \      \           /___
      \______\_________/____"-_
'

snail2='
  @           _________
  |____      /         \
  /    `    /   ____    \  --
  \_    |  /   /    \    \  --
    |   | (    \__/  )    )  --
    \    \_\ \______/    /  --
     \      \           /___
      \______\_________/____"-_
'

snail3='
      @       _________
     /___    /         \
    /    `  /   ____    \ -
    \_   / /   /    \    \ -
     |   |(    \__/  )    ) -
     |   |_\ \______/    / -
     \      \           /___
      \______\_________/____"-_
'

while true;do
    clear
    printf "$snail1"
    sleep 0.5
    clear
    printf "$snail2"
    sleep 0.5
    clear
    printf "$snail3"
    sleep 0.5
    clear
    printf "$snail2"
    sleep 0.5
    clear
    printf "$snail1"
done
