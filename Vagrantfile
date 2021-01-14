Vagrant.configure(2) do |config|
  config.vm.box ="ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 2020, host: 2020
  config.vm.synced_folder ".", "/MathInspector"
  config.vm.provision :shell, :path => "install.sh"
end