[![Build Status](https://travis-ci.org/ICTKyouikukei2013/portbacker.png?branch=tos-kamiya/refactoring)](https://travis-ci.org/ICTKyouikukei2013/portbacker)

# portbacker

## 必要なもの

### Python
* version 2.7

### Flask
* version 0.10.1

### MongoDB
* version 2.4.3
* 参照→ http://nigohiroki.hatenablog.com/entry/2013/01/05/234631

### pymongo
* version 2.5.2

```bash
$ sudo easy_install pymongo
```

## portfolioシステムの起動の仕方

```bash
$ cd portbacker
$ python portfolio.py
```
* → もし起動しない場合は上記のインストールに不備がある
* ブラウザでlocalhost:5000に接続

## portfolioシステムのデータベースをクリアする方法

1. コマンドラインからmongoという対話的にデータベースを操作するコマンドを起動する。
2. user portbackerでportbackerのデータベースを指定する。
3. db.dropDatabase()でデータベースを削除する。

(実行例)

```bash
$ mongo
> use portbacker
switched to db portbacker
> db.dropDatabase()
{ "dropped" : "portbacker", "ok" : 1 }
> show dbs
> quit()
```

## wiki
[wiki](https://github.com/ICTKyouikukei2013/portbacker/wiki "wiki")

### データ構造
[データ構造](https://github.com/ICTKyouikukei2013/portbacker/wiki/%E3%83%87%E3%83%BC%E3%82%BF%E6%A7%8B%E9%80%A0 "データ構造")


