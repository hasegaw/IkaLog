#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  IkaLog
#  ======
#  Copyright (C) 2015 Takeshi HASEGAWA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

#  IkaLog Constants

stages = {
    'anchovy': {'ja': 'アンチョビットゲームズ', 'en': 'Ancho-V Games'},
    'arowana':  {'ja': 'アロワナモール',      'en': 'Arowana mall'},
    'bbass':    {'ja': 'Bバスパーク',         'en': 'Blackbelly Skatepark'},
    'dekaline': {'ja': 'デカライン高架下',    'en': 'Urchin Underpass'},
    'hakofugu': {'ja': 'ハコフグ倉庫',        'en': 'Walleye Warehouse', },
    'hirame':   {'ja': 'ヒラメが丘団地',      'en': 'Flounder Heights', },
    'hokke':    {'ja': 'ホッケふ頭',          'en': 'Port Mackerel'},
    'kinmedai': {'ja': 'キンメダイ美術館',    'en': 'Museum Alfonsino'},
    'mahimahi': {'ja': 'マヒマヒリゾート&スパ', 'en': 'Mahi-Mahi Resort', },
    'masaba':   {'ja': 'マサバ海峡大橋',      'en': 'Hammerhead Bridge', },
    'mongara':  {'ja': 'モンガラキャンプ場',  'en': 'Camp Triggerfish', },
    'mozuku':   {'ja':  'モズク農園',         'en': 'Kelp Dome', },
    'negitoro': {'ja': 'ネギトロ炭鉱',        'en': 'Bulefin Depot', },
    'shionome': {'ja': 'シオノメ油田',        'en': 'Saltspray Rig', },
    'shottsuru': {'ja': 'ショッツル鉱山',     'en': 'Piranha Pit'},
    'tachiuo':  {'ja':  'タチウオパーキング', 'en':  'Moray Towers', },
}

rules = {
    'nawabari': {'ja': 'ナワバリバトル', 'en': 'Turf war', },
    'area': {'ja': 'ガチエリア', 'en': 'Splat Zones', },
    'yagura': {'ja': 'ガチヤグラ', 'en': 'Tower Control', },
    'hoko': {'ja': 'ガチホコバトル', 'en': 'Rainmaker', },
}

weapons = {
    '52gal': {'ja': 'ガロン52'},
    '52gal_deco': {'ja': 'ガロンデコ52'},
    '96gal': {'ja': 'ガロン96'},
    '96gal_deco': {'ja': 'ガロンデコ96'},
    'bold': {'ja': 'ボールドマーカー'},
    'bold_neo': {'ja': 'ボールドマーカーネオ'},
    'dualsweeper': {'ja': 'デュアルスイーパー'},
    'dualsweeper_custom': {'ja': 'デュアルスイーパーカスタム'},
    'h3reelgun': {'ja': 'H3リールガン'},
    'h3reelgun_d': {'ja': 'H3リールガンD'},
    'heroshooter_replica': {'ja': 'ヒーローシューターレプリカ'},
    'hotblaster': {'ja': 'ホットブラスター'},
    'hotblaster_custom': {'ja': 'ホットブラスターカスタム'},
    'jetsweeper': {'ja': 'ジェットスイーパー'},
    'jetsweeper_custom': {'ja': 'ジェットスイーパーカスタム'},
    'l3reelgun': {'ja': 'L3リールガン'},
    'l3reelgun_d': {'ja': 'L3リールガンD'},
    'longblaster': {'ja': 'ロングブラスター'},
    'longblaster_custom': {'ja': 'ロングブラスターカスタム'},
    'momiji': {'ja': 'もみじシューター'},
    'nova': {'ja': 'ノヴァブラスター'},
    'nova_neo': {'ja': 'ノヴァブラスターネオ'},
    'nzap85': {'ja': 'N-ZAP85'},
    'nzap89': {'ja': 'N-ZAP89'},
    'octoshooter_replica': {'ja': 'オクタシューターレプリカ'},
    'prime': {'ja': 'プライムシューター'},
    'prime_collabo': {'ja': 'プライムシューターコラボ'},
    'promodeler_mg': {'ja': 'プロモデラーMG'},
    'promodeler_rg': {'ja': 'プロモデラーRG'},
    'rapid': {'ja': 'ラピッドブラスター'},
    'rapid_deco': {'ja': 'ラピッドブラスターデコ'},
    'rapid_elite': {'ja': 'Rブラスターエリート'},
    'rapid_elite_deco': {'ja': 'Rブラスターエリートデコ'},
    'sharp': {'ja': 'シャープマーカー'},
    'sharp_neo': {'ja': 'シャープマーカーネオ'},
    'sshooter': {'ja': 'スプラシューター'},
    'sshooter_collabo': {'ja': 'スプラシューターコラボ'},
    'wakaba': {'ja': 'わかばシューター'},

    'carbon': {'ja': 'カーボンローラー'},
    'carbon_deco': {'ja': 'カーボンローラーデコ'},
    'dynamo': {'ja': 'ダイナモローラー'},
    'dynamo_tesla': {'ja': 'ダイナモローラーテスラ'},
    'heroroller_replica': {'ja': 'ヒーローローラーレプリカ'},
    'hokusai': {'ja': 'ホクサイ'},
    'pablo': {'ja': 'パブロ'},
    'pablo_hue': {'ja': 'パブロ・ヒュー'},
    'splatroller': {'ja': 'スプラローラー'},
    'splatroller_collabo': {'ja': 'スプラローラーコラボ'},

    'bamboo14mk1': {'ja': '14式竹筒銃・甲'},
    'bamboo14mk2': {'ja': '14式竹筒銃・乙'},
    'herocharger_replica': {'ja': 'ヒーローチャージャーレプリカ'},
    'liter3k': {'ja': 'リッター3K'},
    'liter3k_custom': {'ja': 'リッター3Kカスタム'},
    'liter3k_scope': {'ja': '3Kスコープ'},
    'liter3k_scope_custom': {'ja': '3Kスコープカスタム'},
    'splatcharger': {'ja': 'スプラチャージャー'},
    'splatcharger_wakame': {'ja': 'スプラチャージャーワカメ'},
    'splatscope': {'ja': 'スプラスコープ'},
    'splatscope_wakame': {'ja': 'スプラスコープワカメ'},
    'squiclean_a': {'ja': 'スクイックリンα'},
    'squiclean_b': {'ja': 'スクイックリンβ'},

    'bucketslosher': {'ja': 'バケットスロッシャー'},
    'bucketslosher_deco': {'ja': 'バケットスロッシャーデコ'},
    'hissen': {'ja': 'ヒッセン'},
    'hissen_hue': {'ja': 'ヒッセン・ヒュー'},
    'screwslosher': {'ja': 'スクリュースロッシャー'},

    'barrelspinner': {'ja': 'バレルスピナー'},
    'barrelspinner_deco': {'ja': 'バレルスピナーデコ'},
    'hydra': {'ja': 'ハイドラント'},
    'splatspinner': {'ja': 'スプラスピナー'},
    'splatspinner_collabo': {'ja': 'スプラスピナーコラボ'},
}

sub_weapons = {
    'chasebomb': {'ja': 'チェイスボム', 'en':  'Seeker', },
    'jumpbeacon': {'ja': 'ジャンプビーコン', 'en':  'Squid Beakon', },
    'kyubanbomb': {'ja': 'キューバンボム', 'en':  'Suction Bomb', },
    'pointsensor': {'ja': 'ポイントセンサー', 'en':  'Point Sensor', },
    'poison': {'ja': 'ポイズンボール', 'en':  'Disruptor', },
    'quickbomb': {'ja': 'クイックボム', 'en':  'Burst Bomb', },
    'splashbomb': {'ja': 'スプラッシュボム', 'en':  'Splat Bomb', },
    'splashshield': {'ja': 'スプラッシュシールド', 'en':  'Splash Wall', },
    'sprinkler': {'ja': 'スプリンクラー', 'en':  'Sprinkler', },
    'trap': {'ja': 'トラップ', 'en':  'Ink Mine', },
}

deadly_sub_weapons = [
    'chasebomb', 'kyubanbomb', 'quickbomb', 'splashbomb', 'splashshield',
    'sprinkler', 'trap',
]

special_weapons = {
    'barrier': {'ja': 'バリア', 'en':  'Bubbler', },
    'bombrush': {'ja': 'ボムラッシュ', 'en':  'Bomb Rush', },
    'daioika': {'ja': 'ダイオウイカ', 'en':  'Kraken', },
    'megaphone': {'ja': 'メガホンレーザー', 'en':  'Killer Wail', },
    'supersensor': {'ja': 'スーパーセンサー', 'en':  'Echolocator', },
    'supershot': {'ja': 'スーパーショット', 'en':  'Inkzooka', },
    'tornado': {'ja': 'トルネード', 'en':  'Inkstrike', },
}

deadly_special_weapons = ['daioika', 'megaphone', 'supershot', 'tornado', ]

hoko_attacks = {
    'hoko_shot': {'ja': 'ガチホコショット', 'en': 'Rainmaker Shot', },
    'hoko_barrier': {'ja': 'ガチホコバリア', 'en': 'Rainmaker Shield', },
    'hoko_inksplode': {'ja': 'ガチホコ爆発', 'en': 'Rainmaker Inksplode', },
}

oob_reasons = {
    'oob': {'ja': '場外', 'en': 'Out of Bounds', },
    'fall': {'ja': '転落', 'en': 'Fall', },
    'drown': {'ja': '水死', 'en': 'Drowning', },
}

udemae_strings = [
    's+', 's', 'a+', 'a', 'a-', 'b+', 'b', 'b-', 'c+', 'c', 'c-'
]

fes_rank_titles = [
    'fanboy', 'friend', 'defender', 'champion', 'king'
]

gear_abilities = {
    'bomb_range_up': {'ja': 'ボム飛距離アップ'},
    'bomb_sniffer': {'ja': 'ボムサーチ'},
    'cold_blooded': {'ja': 'マーキングガード'},
    'comeback': {'ja': 'カムバック'},
    'damage_up': {'ja': '攻撃力アップ'},
    'defense_up': {'ja': '防御力アップ'},
    'empty': {'ja': '空'},
    'haunt': {'ja': 'うらみ'},
    'ink_recovery_up': {'ja': 'インク回復力アップ'},
    'ink_resistance_up': {'ja': '安全シューズ'},
    'ink_saver_main': {'ja': 'インク効率アップ（メイン）'},
    'ink_saver_sub': {'ja': 'インク効率アップ（サブ）'},
    'last-ditch_effort': {'ja': 'ラストスパート'},
    'locked': {'ja': '未開放'},
    'ninja_squid': {'ja': 'イカニンジャ'},
    'opening_gambit': {'ja': 'スタートダッシュ'},
    'quick_respawn': {'ja': '復活時間短縮'},
    'quick_super_jump': {'ja': 'スーパージャンプ時間短縮', },
    'recon': {'ja': 'スタートレーダー', },
    'run_speed_up': {'ja': 'ヒト移動速度アップ'},
    'special_charge_up': {'ja':  'スペシャル増加量アップ'},
    'special_duration_up': {'ja':  'スペシャル時間延長', },
    'special_saver': {'ja':  'スペシャル減少量ダウン', },
    'stealth_jump': {'ja':  'ステルスジャンプ', },
    'swim_speed_up': {'ja':  'イカダッシュ速度アップ', },
    'tenacity': {'ja':  '逆境', }
}

for ability in gear_abilities.keys():
    gear_abilities[ability]['id'] = ability
