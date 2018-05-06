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

from ikalog.utils import statink_json

#  IkaLog Constants

stages = {
    'anchovy': {'ja': 'アンチョビットゲームズ', 'en': 'Ancho-V Games'},
    'arowana':  {'ja': 'アロワナモール',      'en': 'Arowana Mall'},
    'bbass':    {'ja': 'Bバスパーク',         'en': 'Blackbelly Skatepark'},
    'dekaline': {'ja': 'デカライン高架下',    'en': 'Urchin Underpass'},
    'hakofugu': {'ja': 'ハコフグ倉庫',        'en': 'Walleye Warehouse', },
    'hirame':   {'ja': 'ヒラメが丘団地',      'en': 'Flounder Heights', },
    'hokke':    {'ja': 'ホッケふ頭',          'en': 'Port Mackerel'},
    'kinmedai': {'ja': 'キンメダイ美術館',    'en': 'Museum d\'Alfonsino'},
    'mahimahi': {'ja': 'マヒマヒリゾート&スパ', 'en': 'Mahi-Mahi Resort', },
    'masaba':   {'ja': 'マサバ海峡大橋',      'en': 'Hammerhead Bridge', },
    'mongara':  {'ja': 'モンガラキャンプ場',  'en': 'Camp Triggerfish', },
    'mozuku':   {'ja':  'モズク農園',         'en': 'Kelp Dome', },
    'negitoro': {'ja': 'ネギトロ炭鉱',        'en': 'Bluefin Depot', },
    'shionome': {'ja': 'シオノメ油田',        'en': 'Saltspray Rig', },
    'shottsuru': {'ja': 'ショッツル鉱山',     'en': 'Piranha Pit'},
    'tachiuo':  {'ja':  'タチウオパーキング', 'en':  'Moray Towers', },
}

rules = {
    'nawabari': {'ja': 'ナワバリバトル', 'en': 'Turf War', },
    'area': {'ja': 'ガチエリア', 'en': 'Splat Zones', },
    'yagura': {'ja': 'ガチヤグラ', 'en': 'Tower Control', },
    'hoko': {'ja': 'ガチホコバトル', 'en': 'Rainmaker', },
    'asari': {'ja': 'ガチアサリ', 'en': 'Cram Blitz', },
}

weapons = {
    '52gal': {'ja': '.52ガロン', 'en': '.52 Gal'},
    '52gal_deco': {'ja': '.52ガロンデコ', 'en': '.52 Gal Deco'},
    '96gal': {'ja': '.96ガロン', 'en': '.96 Gal'},
    '96gal_deco': {'ja': '.96ガロンデコ', 'en': '.96 Gal Deco'},
    'bold': {'ja': 'ボールドマーカー', 'en': 'Sploosh-o-matic'},
    'bold_7': {'ja': 'ボールドマーカー7', 'en': 'Sploosh-o-matic 7'},
    'bold_neo': {'ja': 'ボールドマーカーネオ', 'en': 'Neo Sploosh-o-matic'},
    'dualsweeper': {'ja': 'デュアルスイーパー', 'en': 'Dual Squelcher'},
    'dualsweeper_custom': {'ja': 'デュアルスイーパーカスタム', 'en': 'Custom Dual Squelcher'},
    'h3reelgun': {'ja': 'H3リールガン', 'en': 'H-3 Nozzlenose'},
    'h3reelgun_cherry': {'ja': 'H3リールガンチェリー', 'en': 'Cherry H-3 Nozzlenose'},
    'h3reelgun_d': {'ja': 'H3リールガンD', 'en': 'H-3 Nozzlenose D'},
    'heroshooter_replica': {'ja': 'ヒーローシューターレプリカ', 'en': 'Hero Shot Replica'},
    'hotblaster': {'ja': 'ホットブラスター', 'en': 'Blaster'},
    'hotblaster_custom': {'ja': 'ホットブラスターカスタム', 'en': 'Custom Blaster'},
    'jetsweeper': {'ja': 'ジェットスイーパー', 'en': 'Jet Squelcher'},
    'jetsweeper_custom': {'ja': 'ジェットスイーパーカスタム', 'en': 'Custom Jet Squelcher'},
    'l3reelgun': {'ja': 'L3リールガン', 'en': 'L-3 Nozzlenose'},
    'l3reelgun_d': {'ja': 'L3リールガンD', 'en': 'L-3 Nozzlenose D'},
    'longblaster': {'ja': 'ロングブラスター', 'en': 'Range Blaster'},
    'longblaster_custom': {'ja': 'ロングブラスターカスタム', 'en': 'Custom Range laster'},
    'longblaster_necro': {'ja': 'ロングブラスターネクロ', 'en': 'Grim Range laster'},
    'momiji': {'ja': 'もみじシューター', 'en': 'Custom Splattershot Jr.'},
    'nova': {'ja': 'ノヴァブラスター', 'en': 'Luna Blaster'},
    'nova_neo': {'ja': 'ノヴァブラスターネオ', 'en': 'Luna Blaster Neo'},
    'nzap83': {'ja': 'N-ZAP83', 'en': 'N-ZAP \'83'},
    'nzap85': {'ja': 'N-ZAP85', 'en': 'N-ZAP \'85'},
    'nzap89': {'ja': 'N-ZAP89', 'en': 'N-Zap \'89'},
    'octoshooter_replica': {'ja': 'オクタシューターレプリカ', 'en': 'Octoshot Replica'},
    'prime': {'ja': 'プライムシューター', 'en': 'Splattershot Pro'},
    'prime_berry': {'ja': 'プライムシューターベリー', 'en': 'Berry Splattershot Pro'},
    'prime_collabo': {'ja': 'プライムシューターコラボ', 'en': 'Forge Splattershot Pro'},
    'promodeler_mg': {'ja': 'プロモデラーMG', 'en': 'Aerospray MG'},
    'promodeler_pg': {'ja': 'プロモデラーPG', 'en': 'Aerospray PG'},
    'promodeler_rg': {'ja': 'プロモデラーRG', 'en': 'Aerospray RG'},
    'rapid': {'ja': 'ラピッドブラスター', 'en': 'Rapid Blaster'},
    'rapid_deco': {'ja': 'ラピッドブラスターデコ', 'en': 'Rapid Blaster Deco'},
    'rapid_elite': {'ja': 'Rブラスターエリート', 'en': 'Rapid Blaster Pro'},
    'rapid_elite_deco': {'ja': 'Rブラスターエリートデコ', 'en': 'Rapid Blaster Pro Deco'},
    'sharp': {'ja': 'シャープマーカー', 'en': 'Splash-o-matic'},
    'sharp_neo': {'ja': 'シャープマーカーネオ', 'en': 'Neo Splash-o-matic'},
    'sshooter': {'ja': 'スプラシューター', 'en': 'Splattershot'},
    'sshooter_collabo': {'ja': 'スプラシューターコラボ', 'en': 'Tentatek Splattershot'},
    'sshooter_wasabi': {'ja': 'スプラシューターワサビ', 'en': 'Wasabi Splattershot'},
    'wakaba': {'ja': 'わかばシューター', 'en': 'Splattershot Jr.'},

    'carbon': {'ja': 'カーボンローラー', 'en': 'Carbon Roller'},
    'carbon_deco': {'ja': 'カーボンローラーデコ', 'en': 'Carbon Roller Deco'},
    'dynamo': {'ja': 'ダイナモローラー', 'en': 'Dynamo Roller'},
    'dynamo_burned': {'ja': 'ダイナモローラーバーンド', 'en': 'Tempered Dynamo Roller'},
    'dynamo_tesla': {'ja': 'ダイナモローラーテスラ', 'en': 'Gold Dynamo Roller'},
    'heroroller_replica': {'ja': 'ヒーローローラーレプリカ', 'en': 'Hero Roller Replica'},
    'hokusai': {'ja': 'ホクサイ', 'en': 'Octobrush'},
    'hokusai_hue': {'ja': 'ホクサイ・ヒュー', 'en': 'Octobrush Nouveau'},
    'pablo': {'ja': 'パブロ', 'en': 'Inkbrush'},
    'pablo_hue': {'ja': 'パブロ・ヒュー', 'en': 'Inkbrush Nouveau'},
    'pablo_permanent': {'ja': 'パーマネント・パブロ', 'en': 'Permanent Inkbrush'},
    'splatroller': {'ja': 'スプラローラー', 'en': 'Splat Roller'},
    'splatroller_collabo': {'ja': 'スプラローラーコラボ', 'en': 'Krak-On Splat Roller'},
    'splatroller_corocoro': {'ja': 'スプラローラーコロコロ', 'en': 'CoroCoro Splat Roller'},

    'bamboo14mk1': {'ja': '14式竹筒銃・甲', 'en': 'Bamboozler 14 MK I'},
    'bamboo14mk2': {'ja': '14式竹筒銃・乙', 'en': 'Bamboozler 14 MK II'},
    'bamboo14mk3': {'ja': '14式竹筒銃・丙', 'en': 'Bamboozler 14 Mk III'},
    'herocharger_replica': {'ja': 'ヒーローチャージャーレプリカ', 'en': 'Hero Charger Replica'},
    'liter3k': {'ja': 'リッター3K', 'en': 'E-liter 3K'},
    'liter3k_custom': {'ja': 'リッター3Kカスタム', 'en': 'Custom E-liter 3K'},
    'liter3k_scope': {'ja': '3Kスコープ', 'en': 'E-liter 3K Scope'},
    'liter3k_scope_custom': {'ja': '3Kスコープカスタム', 'en': 'Custom E-liter 3K Scope'},
    'splatcharger': {'ja': 'スプラチャージャー', 'en': 'Splat Charger'},
    'splatcharger_bento': {'ja': 'スプラチャージャーベントー', 'en': 'Bento Splat Charger'},
    'splatcharger_wakame': {'ja': 'スプラチャージャーワカメ', 'en': 'Kelp Splat Charger'},
    'splatscope': {'ja': 'スプラスコープ', 'en': 'Splatterscope'},
    'splatscope_bento': {'ja': 'スプラスコープベントー', 'en': 'Bento Splatterscope'},
    'splatscope_wakame': {'ja': 'スプラスコープワカメ', 'en': 'Kelp Splatterscope'},
    'squiclean_a': {'ja': 'スクイックリンα', 'en': 'Classic Squiffer'},
    'squiclean_b': {'ja': 'スクイックリンβ', 'en': 'New Squiffer'},
    'squiclean_g': {'ja': 'スクイックリンγ', 'en': 'Fresh Squiffer'},

    'bucketslosher': {'ja': 'バケットスロッシャー', 'en': 'Slosher'},
    'bucketslosher_deco': {'ja': 'バケットスロッシャーデコ', 'en': 'Slosher Deco'},
    'bucketslosher_soda': {'ja': 'バケットスロッシャーソーダ', 'en': 'Soda Slosher'},
    'hissen': {'ja': 'ヒッセン', 'en': 'Tri-Slosher'},
    'hissen_hue': {'ja': 'ヒッセン・ヒュー', 'en': 'Tri-Slosher Nouveau'},
    'screwslosher': {'ja': 'スクリュースロッシャー', 'en': 'Sloshing Machine'},
    'screwslosher_neo': {'ja': 'スクリュースロッシャーネオ', 'en': 'Sloshing Machine Neo'},

    'barrelspinner': {'ja': 'バレルスピナー', 'en': 'Heavy Splatling'},
    'barrelspinner_deco': {'ja': 'バレルスピナーデコ', 'en': 'Heavy Splatling Deco'},
    'barrelspinner_remix': {'ja': 'バレルスピナーリミックス', 'en': 'Heavy Splatling Remix'},
    'hydra': {'ja': 'ハイドラント', 'en': 'Hydra Splatling'},
    'hydra_custom': {'ja': 'ハイドラントカスタム', 'en': 'Custom Hydra Splatling'},
    'splatspinner': {'ja': 'スプラスピナー', 'en': 'Mini Splatling'},
    'splatspinner_collabo': {'ja': 'スプラスピナーコラボ', 'en': 'Zink Mini Splatling'},
    'splatspinner_repair': {'ja': 'スプラスピナーリペア', 'en': 'Refurbished Mini Splatling'},
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

hurtable_objects = {
    'hoko_shot': {'ja': 'ガチホコショット', 'en': 'Rainmaker Shot', },
    'hoko_barrier': {'ja': 'ガチホコバリア', 'en': 'Rainmaker Shield', },
    'hoko_inksplode': {'ja': 'ガチホコ爆発', 'en': 'Rainmaker Inksplode', },

    'propeller': {'ja': 'プロペラから飛び散ったインク', 'en': 'Ink from a propeller'},
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
    'fanboy', 'fiend', 'defender', 'champion', 'king'
]


gear_abilities = {
    'bomb_range_up': {'ja': 'ボム飛距離アップ', 'en': 'Bomb Range Up'},
    'bomb_sniffer': {'ja': 'ボムサーチ', 'en': 'Bomb Sniffer'},
    'cold_blooded': {'ja': 'マーキングガード', 'en': 'Cold Blooded'},
    'comeback': {'ja': 'カムバック', 'en': 'Comeback'},
    'damage_up': {'ja': '攻撃力アップ', 'en': 'Damage Up'},
    'defense_up': {'ja': '防御力アップ', 'en': 'Defense Up'},
    'empty': {'ja': '空', 'en': 'Empty'},
    'haunt': {'ja': 'うらみ', 'en': 'Haunt'},
    'ink_recovery_up': {'ja': 'インク回復力アップ', 'en': 'Ink Recovery Up'},
    'ink_resistance_up': {'ja': '安全シューズ', 'en': 'Ink Resistance'},
    'ink_saver_main': {'ja': 'インク効率アップ（メイン）', 'en': 'Ink Saver (Main)'},
    'ink_saver_sub': {'ja': 'インク効率アップ（サブ）', 'en': 'Ink Saver (Sub)'},
    'last_ditch_effort': {'ja': 'ラストスパート', 'en': 'Last-Ditch Effort'},
    'locked': {'ja': '未開放', 'en': 'Locked'},
    'ninja_squid': {'ja': 'イカニンジャ', 'en': 'Ninja Squid'},
    'opening_gambit': {'ja': 'スタートダッシュ', 'en': 'Opening Gambit'},
    'quick_respawn': {'ja': '復活時間短縮', 'en': 'Quick Respawn'},
    'quick_super_jump': {'ja': 'スーパージャンプ時間短縮', 'en': 'Quick Super Jump'},
    'recon': {'ja': 'スタートレーダー', 'en': 'Recon'},
    'run_speed_up': {'ja': 'ヒト移動速度アップ', 'en': 'Run Speed Up'},
    'special_charge_up': {'ja':  'スペシャル増加量アップ', 'en': 'Special Charge Up'},
    'special_duration_up': {'ja':  'スペシャル時間延長', 'en': 'Special Duration Up'},
    'special_saver': {'ja':  'スペシャル減少量ダウン', 'en': 'Special Saver'},
    'stealth_jump': {'ja':  'ステルスジャンプ', 'en': 'Stealth Jump'},
    'swim_speed_up': {'ja':  'イカダッシュ速度アップ', 'en': 'Swim Speed Up'},
    'tenacity': {'ja':  '逆境', 'en': 'Tenacity'}
}

gear_brands = {
    'amiibo':     {'ja': 'amiibo', 'en': 'amiibo', },
    'cuttlegear': {'ja': 'アタリメイド', 'en': 'Cuttlegear', },
    'famitsu':    {'ja': 'ファミ通', 'en': 'Famitsu', },
    'firefin':    {'ja': 'ホッコリー', 'en': 'Firefin', },
    'forge':      {'ja': 'Forge', 'en': 'Forge', },
    'inkline':    {'ja': 'Inkline', 'en': 'Inkline', },
    'kog':        {'ja': 'KOG', 'en': 'KOG', },
    'krakon':     {'ja': 'クラーゲス', 'en': 'Krak-On', },
    'rockenberg': {'ja': 'ロッケンベルグ', 'en': 'Rockenberg', },
    'skalop':     {'ja': 'ホタックス', 'en': 'Skalop', },
    'splashmob':  {'ja': 'ジモン', 'en': 'Splash Mob', },
    'squidforce': {'ja': 'バトロイカ', 'en': 'Squidforce', },
    'squidgirl':  {'ja': '侵略！イカ娘', 'en': 'SQUID GIRL', },
    'takoroka':   {'ja': 'ヤコ', 'en': 'Takoroka', },
    'tentatek':   {'ja': 'アロメ', 'en': 'Tentatek', },
    'zekko':      {'ja': 'エゾッコ', 'en': 'Zekko', },
    'zink':       {'ja': 'アイロニック', 'en': 'Zink', },
}

lobby_types = {
    'festa':    {'ja': 'フェス', 'en': 'Splatfest'},
    'private':  {'ja': 'プライベートマッチ', 'en': 'Private Battle'},
    'public':   {'ja': '通常マッチ', 'en': 'Standard Battle'},
    'tag':      {'ja': 'タッグマッチ', 'en': 'Squad Battle'},
}

#

upcoming_weapons = [
]

#

for ability in gear_abilities.keys():
    gear_abilities[ability]['id'] = ability

for brand in gear_brands.keys():
    gear_brands[brand]['id'] = brand

#

stages_v1 = statink_json.import_stages('data/spl1/stages.json')
weapons_v1 = statink_json.import_weapons('data/spl1/weapons.json')
stages_v2 = statink_json.import_stages('data/spl2/stages.json')
weapons_v2 = statink_json.import_weapons('data/spl2/weapons.json')
