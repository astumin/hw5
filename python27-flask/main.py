#!/usr/bin/env python
# -*- coding: utf-8 -*-
# コマンド dev_appserver.py python27-flask/

from google.appengine.api import urlfetch
import json
from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True

networkJson = urlfetch.fetch("http://tokyo.fantasy-transit.appspot.com/net?format=json").content  # ウェブサイトから電車の線路情報をJSON形式でダウンロードする
network = json.loads(networkJson.decode('utf-8'))  # JSONとしてパースする（stringからdictのlistに変換する）

# ページから値を取得する
def getstation(stationas):
      return request.args.get(stationas)

# 隣接リスト辞書型で生成
def makemap(network):
    trainmap={}
    for i in network:
        forwardstation = None
        for j in i["Stations"]:
            if forwardstation != None:
                if j not in trainmap:
                    trainmap[j]={}
                trainmap[j][forwardstation] = i["Name"]+"UP"
                if forwardstation not in trainmap:
                    trainmap[forwardstation] = {}
                trainmap[forwardstation][j] = i["Name"]+"DOWN"
            forwardstation = j
    
    return trainmap

# 幅優先探索で得たデータを元に経路データを得る
def makepath(listpaths,paths,map):
    path = {}
    path["GOAL"] = "GOAL"
    station = listpaths.pop("GOAL")
    nextstation = station
    stationlist = [station]
    while(1):
        station = listpaths.pop(station)
        path[nextstation] = paths[nextstation][station]
        nextstation = station
        if station == "START":
            break
        stationlist.append(station)
    stationlist.reverse()
    return path, stationlist

# 幅優先探索で経路データを取得
# 得られるデータは出発地点・到着地点・使った路線をまとめた辞書型(queue)と出発地点と到着地点をまとめた辞書型(listque)を返す
def BFSsearchpath(start ,goal, trainmap):
    # quelistの中身は　[渋谷]、[原宿、恵比寿]、...
    quelist = [start] 
    
    # queueの中身は、'学芸大学': {'祐天寺': '東横線UP'}  東横線UPを使って祐天寺から学芸大学にいけるという意味
    queue = {}
    listque = {}
    queue[start] = {}
    queue[start]["START"]="START" 
    listque[start]="START"

    # checkedのなかみは、　[渋谷、原宿...]
    # すでに処理した駅の一覧
    checked = set()
    while(1):
        a = quelist.pop(0)
        checked.add(a)
        if a == goal:
            queue["GOAL"] = {}
            queue["GOAL"][a]="GOAL" 
            listque["GOAL"] = a
            break
        for i in trainmap[a]:
            if i not in checked:
                queue[i]= {}
                queue[i][a] = trainmap[a][i]
                listque[i] = a
                quelist.append(i)
    return listque, queue

# 出発駅・到着駅・路線データを受け取って経路を返す関数
def searchline(start, goal ,linemap):
    listque, que = BFSsearchpath(start, goal , linemap) # 幅優先で経路データを取得する
    path = makepath(listque, que, linemap) # 取得したデータから到着駅から遡って経路を取得する
    return path

@app.route('/')
# / のリクエスト（例えば http://localhost:8080/ ）をこの関数で処理する。
# ここでメニューを表示をしているだけです。
def root():
  return render_template('hello.html')

@app.route('/pata')
# /pata のリクエスト（例えば http://localhost:8080/pata ）をこの関数で処理する。
# これをパタトクカシーーを処理するようにしています。
def pata():
  # とりあえずAとBをつなぐだけで返事を作っていますけど、パタタコカシーーになるように自分で直してください！
  A = request.args.get('a', '')
  B = request.args.get('b', '')
  patalist = []
  if len(A)<len(B):
        num = len(A)
        for a in range(len(A)):
              patalist.append(A[a]+B[a])
        patalist.append(B[len(A):])
  else:
        num = len(B)
        for a in range(num):
              patalist.append(A[a]+B[a])
        patalist.append(A[num:])
  pata = ''.join(patalist)
  # pata.htmlのテンプレートの内容を埋め込んで、返事を返す。
  return render_template('pata.html', pata=pata)

@app.route('/norikae')
# /norikae のリクエスト（例えば http://localhost:8080/norikae ）をこの関数で処理する。
# ここで乗り換え案内をするように編集してください。
def norikae():
  return render_template('norikae.html', network=network)


@app.route('/search')
def search():
  fromstation = getstation("from") # 出発駅の受け取る
  tostation = getstation("to") # 目的地の受け取り
  trainmap = makemap(network) # 路線データから幅優先探索をしやすいようにデータを生成（隣接リスト）
  path, stationlist= searchline(fromstation, tostation, trainmap) # 到着駅までの乗換を探索
  return render_template('search.html', fromstation = fromstation, tostation = tostation, stationlist = stationlist, paths = path)