# 使用Git bash切换Gitee、GitHub多个Git账号

------

# 使用Git bash切换Gitee、GitHub多个Git账号

Git是分布式代码管理工具，使用命令行的方式提交commit、revert回滚代码。这里介绍使用Git bash软件来切换Gitee、GitHub账号。

| 账号 | 名称 |    邮箱    |                   网站                    |
| :--: | :--: | :--------: | :---------------------------------------: |
|  1   | mqx  | 310@qq.com |  [https://gitee.com](https://gitee.com/)  |
|  2   | 310  | 310@qq.com | [https://github.com](https://github.com/) |

### 1、安装Git软件

官网地址：[Git - Windows 安装](https://git-scm.com/install/windows)

### 2、通过邮箱生成公私钥

使用管理员身份打开Git bash软件，然后根据邮箱来生成rsa公钥、私钥文件，命令如下：

- 通过ssh-keygen命令，来生成邮箱对应的公钥、私钥文件：

```bash
31054@▒▒▒▒▒▒ MINGW64 ~
$ ssh-keygen -t rsa -f ~/.ssh/id_rsa_gitee -C "mqx@310@qq.com"
31054@▒▒▒▒▒▒ MINGW64 ~
$ ssh-keygen -t rsa -f ~/.ssh/id_rsa_github -C "310@310@qq.com"
```

- 公钥、私钥文件地址

``` bash
Your identification has been saved in /d/Software/Cadence/SPB_Data/.ssh/id_rsa_gitee
Your public key has been saved in /d/Software/Cadence/SPB_Data/.ssh/id_rsa_gitee.pub
Your identification has been saved in /d/Software/Cadence/SPB_Data/.ssh/id_rsa_github
Your public key has been saved in /d/Software/Cadence/SPB_Data/.ssh/id_rsa_github.pub
```

### 3、将公钥设置到网站的SSH框框里

### 4 、在Git Bash里激活公钥，并授权

继续在Git Bash黑框框里，激活公钥，并授权访问gitee或github。

#### 4.1 激活并授权gitee账号

``` bash
## 1) 激活公钥
ssh -T git@gitee.com -i ~/.ssh/id_rsa_gitee
```

#### 4.2 激活并授权github账号

```bash
## 1) 激活公钥
ssh -T git@github.com -i ~/.ssh/id_rsa_github
```

### 5 、将私钥文件添加到git

#### 5.1 将gitee的私钥文件添加到git

``` bash
## 添加到git
ssh -add ~/.ssh/id_rsa_gitee
```

#### 5.2 将github的私钥文件添加到git

``` bash
## 添加到git
ssh -add ~/.ssh/id_rsa_gitee
```

#### 5.3 报错：如果出现“Could not open a connection to your authentication agent.”的错误

```bash
31054@▒▒▒▒▒▒ MINGW64 ~
$ ssh-add ~/.ssh/id_rsa_gitee
Could not open a connection to your authentication agent.
```

使用如下命令解决：

``` bash
31054@▒▒▒▒▒▒ MINGW64 ~
$ eval `ssh-agent -s`
Agent pid 1092
```

### 6 、配置config文件

<!--config文件，一般保存在~/.ssh/目录里，用于切换多个gitee、github账号-->

#### 6.1 创建config文件

``` bash
## 创建config文件
31054@▒▒▒▒▒▒ MINGW64 ~
$ touch ~/.ssh/config
```

#### 6.2 填写要切换的账号和网站

文件~/.ssh/config的内容如下：

``` bash
Host useEE
HostName gitee.com
IdentityFile D:\\Software\\Cadence\\SPB_Data\\.ssh\\id_rsa_gitee
PreferredAuthentications publickey
User useEE


Host useHub
HostName github.com
IdentityFile D:\\Software\\Cadence\\SPB_Data\\.ssh\\id_rsa_github
PreferredAuthentications publickey
User useHub
```

<!--其中，useEE对应mqx, useHub对应310。-->

就可以正常使用git命令推送到远程仓库等操作。

### 7 、拉取 工程

#### 7.1 拉取gitee上的text1工程

``` bash
git clone git@gitee.com:mqx/text1.git
改成：
git clone git@useEE:mqx/text1.git
```

#### 7.2 拉取github上的text1工程

``` bash
git clone git@github.com:310/text1.git
改成：
git clone git@useHub:310/text1.git
```

