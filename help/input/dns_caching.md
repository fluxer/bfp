## Things you should know before getting started

DNS caching is supposed to boost your internet experience, however it may not
get you the results you are expecting.

## Tools of the trade

Source Package Manager is the package manager that Tiny GNU/Linux uses. If you
are not familiar with it read [this](spm.html) page.

##Getting your hands dirty

As **root**:

    spm repo -cs && spm source -aDu dnsmasq

Set the addres and cache size to be used by dnsmasq:

    sed -e 's|.*listen-address=.*|listen-address=127.0.0.1|g' \
        -e 's|.*cache-size=.*|cache-size=500|g' \
        -i /etc/dnsmasq.conf

Tell dhcpcd to append the address to resolv.conf every time it dumps it, for
an example during system initialization:

    echo 'new_domain_name_servers="127.0.0.1 ${new_domain_name_servers}"' > /lib/dhcpcd/dhcpcd-hooks/19-dnsmasq

Edit /etc/rc.conf and add ''dnsmasq'' in the DAEMONS array. Then start the
dnsmasq daemon:

    rc.d start dnsmasq
