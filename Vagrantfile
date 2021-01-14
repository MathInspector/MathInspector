# use the following command to ssh into the vagrant server to setup x11 forwarding
# $ ssh -X -p 2222 -i .vagrant/machines/default/virtualbox/private_key vagrant@localhost

Vagrant.configure(2) do |config|
  config.vm.box ="ubuntu/bionic64"
  config.vm.network "forwarded_port", guest: 2020, host: 2020
  config.vm.synced_folder ".", "/MathInspector"
  config.vm.provision :shell, :path => "install.sh"
  config.ssh.forward_x11 = true
end