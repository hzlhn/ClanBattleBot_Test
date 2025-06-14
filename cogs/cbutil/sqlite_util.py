import sqlite3
from collections import defaultdict
from typing import DefaultDict, List, Optional

from cogs.cbutil.attack_type import ATTACK_TYPE_DICT
from cogs.cbutil.boss_status_data import AttackStatus, BossStatusData
from cogs.cbutil.clan_data import ClanData
from cogs.cbutil.player_data import CarryOver, PlayerData
from cogs.cbutil.reserve_data import ReserveData
from setup import DB_NAME, JST

sqlite3.dbapi2.converters['DATETIME'] = sqlite3.dbapi2.converters['TIMESTAMP']


REGISTER_CLANDATA_SQL = """insert into ClanData values (
    :guild_id,
    :category_id,
    :boss1_channel_id,
    :boss2_channel_id,
    :boss3_channel_id,
    :boss4_channel_id,
    :boss5_channel_id,
    :remain_attack_channel_id,
    :reserve_channel_id,
    :command_channel_id,
    :boss1_reserve_message_id,
    :boss2_reserve_message_id,
    :boss3_reserve_message_id,
    :boss4_reserve_message_id,
    :boss5_reserve_message_id,
    :remain_attack_message_id,
    :summary_channel_id,
    :day
)"""
UPDATE_CLANDATA_SQL = """update ClanData
    set
        boss1_reserve_message_id=?,
        boss2_reserve_message_id=?,
        boss3_reserve_message_id=?,
        boss4_reserve_message_id=?,
        boss5_reserve_message_id=?,
        remain_attack_message_id=?,
        day=?
    where
        category_id=?"""
DELETE_CLANDATA_SQL = """delete from ClanData where category_id=?"""
REGISTER_PLAYERDATA_SQL = """insert into PlayerData values (
    :category_id,
    :user_id,
    0,
    0,
    0
)"""
UPDATE_PLAYERDATA_SQL = """update PlayerData
    set
        physics_attack=?,
        magic_attack=?,
        task_kill=?
    where
        category_id=? and user_id=?
"""
DELETE_PLAYERDATA_SQL = """DELETE FROM PlayerData
    where
        category_id=? and user_id=?
"""
DELETE_PLAYERDATA_FROM_RESERVEDATA_SQL = """DELETE FROM ReserveData
    where
        category_id=? and user_id=?
"""
DELETE_PLAYERDATA_FROM_ATTACKSTATUS_SQL = """DELETE FROM AttackStatus
    where
        category_id=? and user_id=?
"""
DELETE_PLAYERDATA_FROM_CARRYOVER_SQL = """DELETE FROM CarryOver
    where
        category_id=? and user_id=?
"""
REGISTER_RESERVEDATA_SQL = """insert into ReserveData values (
    :category_id,
    :boss_index,
    :user_id,
    :attack_type,
    :damage,
    :memo,
    :carry_over
)"""
UPDATE_RESERVEDATA_SQL = """update ReserveData
    set
        damage=?,
        memo=?,
        carry_over=?
    where
        category_id=? and boss_index=? and user_id=? and attack_type=?"""
DELETE_RESERVEDATA_SQL = """delete from ReserveData
where
    category_id=? and boss_index=? and user_id=? and attack_type=? and carry_over=?"""
REGISTER_ATTACKSTATUS_SQL = """insert into AttackStatus values (
    :category_id,
    :user_id,
    :lap,
    :boss_index,
    :damage,
    :memo,
    :attacked,
    :attack_type,
    :carry_over,
    :created
)"""
UPDATE_ATTACKSTATUS_SQL = """update AttackStatus
    set
        damage=?,
        memo=?,
        attacked=?,
        attack_type=?
    where
        category_id=? and user_id=? and lap=? and boss_index=? and created=?"""
REVERSE_ATTACKSTATUS_SQL = """update AttackStatus
    set
        attacked=0
    where
        category_id=? and user_id=? and lap=? and boss_index=? and created=?
"""
DELETE_ATTACKSTATUS_SQL = """delete from AttackStatus
    where
        category_id=? and user_id=? and lap=? and boss_index=? and created=?"""
REGISTER_BOSS_STATUS_DATA_SQL = """insert into BossStatusData values (
    :category_id,
    :boss_index,
    :lap,
    :beated
)"""
UPDATE_BOSS_STATUS_DATA_SQL = """update BossStatusData
    set
        beated=?
    where
        category_id=? and boss_index=? and lap=?
"""
DELETE_BOSS_STATUS_DATA_SQL = """delete from BossStatusData
where
    category_id=? and boss_index=?"""
DELETE_ALL_BOSS_STATUS_DATA_SQL = """delete from BossStatusData
where
    category_id=?"""
REGISTER_CARRYOVER_DATA_SQL = """insert into CarryOver values (
    :category_id,
    :user_id,
    :boss_index,
    :attack_type,
    :carry_over_time,
    :created
);"""
UPDATE_CARRYOVER_DATA_SQL = """update CarryOver
    set
        carry_over_time=?
    where
        category_id=? and user_id=? and created=?"""
DELETE_CARRYOVER_DATA_SQL = """delete from CarryOver
where
    category_id=? and user_id=? and created=?"""
DELETE_ALL_CARRYOVER_DATA_SQL = """delete from CarryOver
where
    category_id=? and user_id=?"""
REGISTER_FORMDATA_SQL = """insert into FormData values (
    :category_id,
    :form_url,
    :sheet_url,
    :name_entry,
    :discord_id_entry,
    :created
)"""
UPDATE_FORMDATA_SQL = """update FormData
    set
        form_url=?,
        sheet_url=?,
        name_entry=?,
        discord_id_entry=?,
        created=?
    where
        category_id=?"""
REGISTER_PROGRESS_MESSAGEID_DATA = """
insert into ProgressMessageIdData values (
    :category_id,
    :lap,
    :boss1,
    :boss2,
    :boss3,
    :boss4,
    :boss5
)"""
UPDATE_PROGRESS_MESSAGEID_DATA = """
update ProgressMessageIdData
    set
        boss1=?,
        boss2=?,
        boss3=?,
        boss4=?,
        boss5=?
    where
        category_id=? and lap=?"""
REGISTER_SUMMARY_MESSAGEID_DATA = """
insert into SummaryMessageIdData values (
    :category_id,
    :lap,
    :boss1,
    :boss2,
    :boss3,
    :boss4,
    :boss5
)"""
UPDATE_SUMMARY_MESSAGE_DATA = """
update SummaryMessageIdData
    set
        boss1=?,
        boss2=?,
        boss3=?,
        boss4=?,
        boss5=?
    where
        category_id=? and lap=?"""
DELETE_OLD_SUMMARY_MESSAGE_DATA = """DELETE FROM SummaryMessageIdData
where
    category_id=? and lap<?"""
DELETE_OLD_PROGRESS_MESSAGE_DATA = """DELETE FROM ProgressMessageIdData
where
    category_id=? and lap<?"""
DELETE_OLD_ATTACK_STATUS_DATA = """DELETE FROM AttackStatus
where
    category_id=? and lap<?"""
DELETE_OLD_BOSS_STATUS_DATA = """DELETE FROM BossStatusData
where
    category_id=? and lap<?"""

class SQLiteUtil():
    con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    @staticmethod
    def register_clandata(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(REGISTER_CLANDATA_SQL, (
            clan_data.guild_id,
            clan_data.category_id,
            clan_data.boss_channel_ids[0],
            clan_data.boss_channel_ids[1],
            clan_data.boss_channel_ids[2],
            clan_data.boss_channel_ids[3],
            clan_data.boss_channel_ids[4],
            clan_data.remain_attack_channel_id,
            clan_data.reserve_channel_id,
            clan_data.command_channel_id,
            clan_data.reserve_message_ids[0],
            clan_data.reserve_message_ids[1],
            clan_data.reserve_message_ids[2],
            clan_data.reserve_message_ids[3],
            clan_data.reserve_message_ids[4],
            clan_data.remain_attack_message_id,
            clan_data.summary_channel_id,
            clan_data.date,
        ))
        con.commit()
        con.close()

    @staticmethod
    def update_clandata(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(UPDATE_CLANDATA_SQL, (
            clan_data.reserve_message_ids[0],
            clan_data.reserve_message_ids[1],
            clan_data.reserve_message_ids[2],
            clan_data.reserve_message_ids[3],
            clan_data.reserve_message_ids[4],
            clan_data.remain_attack_message_id,
            clan_data.date,
            clan_data.category_id,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_clandata(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_CLANDATA_SQL, (
            clan_data.category_id,
        ))
        con.commit()
        con.close()

    @staticmethod
    def register_playerdata(clan_data: ClanData, player_data_list: List[PlayerData]):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        records = [(clan_data.category_id, player_data.user_id) for player_data in player_data_list]
        cur = con.cursor()
        cur.executemany(REGISTER_PLAYERDATA_SQL, records)
        con.commit()
        con.close()

    @staticmethod
    def update_playerdata(clan_data: ClanData, player_data: PlayerData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(UPDATE_PLAYERDATA_SQL, (
            player_data.physics_attack,
            player_data.magic_attack,
            player_data.task_kill,
            clan_data.category_id,
            player_data.user_id,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_playerdata(clan_data: ClanData, player_data: PlayerData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        # 全てのテーブルからplayer dataに関するものを削除する。
        cur.execute(DELETE_PLAYERDATA_SQL, (
            clan_data.category_id,
            player_data.user_id,
        ))
        cur.execute(DELETE_PLAYERDATA_FROM_CARRYOVER_SQL, (
            clan_data.category_id,
            player_data.user_id,
        ))
        cur.execute(DELETE_PLAYERDATA_FROM_ATTACKSTATUS_SQL, (
            clan_data.category_id,
            player_data.user_id,
        ))
        cur.execute(DELETE_PLAYERDATA_FROM_RESERVEDATA_SQL, (
            clan_data.category_id,
            player_data.user_id,
        ))
        con.commit()
        con.close()

    @staticmethod
    def register_reservedata(clan_data: ClanData, boss_index: int, reserve_data: ReserveData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(REGISTER_RESERVEDATA_SQL, (
            clan_data.category_id,
            boss_index,
            reserve_data.player_data.user_id,
            reserve_data.attack_type.value,
            reserve_data.damage,
            reserve_data.memo,
            reserve_data.carry_over,
        ))
        con.commit()
        con.close()

    @staticmethod
    def update_reservedata(clan_data: ClanData, boss_index: int, reserve_data: ReserveData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(UPDATE_RESERVEDATA_SQL, (
            reserve_data.damage,
            reserve_data.memo,
            clan_data.category_id,
            boss_index,
            reserve_data.player_data.user_id,
            reserve_data.attack_type.value,
            reserve_data.carry_over,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_reservedata(clan_data: ClanData, boss_index: int, reserve_data: ReserveData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_RESERVEDATA_SQL, (
            clan_data.category_id,
            boss_index,
            reserve_data.player_data.user_id,
            reserve_data.attack_type.value,
            reserve_data.carry_over
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_all_reservedata(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute("delete from ReserveData where category_id=?", (clan_data.category_id,))
        con.commit()
        con.close()

    @staticmethod
    def register_attackstatus(clan_data: ClanData, lap: int, boss_index: int, attack_status: AttackStatus):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(REGISTER_ATTACKSTATUS_SQL, (
            clan_data.category_id,
            attack_status.player_data.user_id,
            lap,
            boss_index,
            attack_status.damage,
            attack_status.memo,
            attack_status.attacked,
            attack_status.attack_type.value,
            attack_status.carry_over,
            attack_status.created,
        ))
        con.commit()
        con.close()

    @staticmethod
    def update_attackstatus(clan_data: ClanData, lap: int, boss_index: int, attack_status: AttackStatus):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(UPDATE_ATTACKSTATUS_SQL, (
            attack_status.damage,
            attack_status.memo,
            attack_status.attacked,
            attack_status.attack_type.value,
            clan_data.category_id,
            attack_status.player_data.user_id,
            lap,
            boss_index,
            attack_status.created,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_attackstatus(clan_data: ClanData, lap: int, boss_index: int, attack_status: AttackStatus):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_ATTACKSTATUS_SQL, (
            clan_data.category_id,
            attack_status.player_data.user_id,
            lap,
            boss_index,
            attack_status.created,
        ))
        con.commit()
        con.close()

    @staticmethod
    def reverse_attackstatus(clan_data: ClanData, lap: int, boss_index: int, attack_status: AttackStatus):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(REVERSE_ATTACKSTATUS_SQL, (
            clan_data.category_id,
            attack_status.player_data.user_id,
            lap,
            boss_index,
            attack_status.created,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_all_attackstatus(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute("delete from AttackStatus where category_id=?", (clan_data.category_id,))
        con.commit()

    @staticmethod
    def register_boss_status_data(clan_data: ClanData, boss_index: int, boss_status_data: BossStatusData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(REGISTER_BOSS_STATUS_DATA_SQL, (
            clan_data.category_id,
            boss_index,
            boss_status_data.lap,
            boss_status_data.beated,
        ))
        con.commit()
        con.close()

    @staticmethod
    def register_all_boss_status_data(clan_data: ClanData, lap: int):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        records = [
            (clan_data.category_id, i, lap, boss_status_data.beated)
            for i, boss_status_data in enumerate(clan_data.boss_status_data[lap])]
        cur.executemany(REGISTER_BOSS_STATUS_DATA_SQL, records)
        con.commit()
        con.close()

    @staticmethod
    def update_boss_status_data(clan_data: ClanData, boss_index: int, boss_status_data: BossStatusData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(UPDATE_BOSS_STATUS_DATA_SQL, (
            boss_status_data.beated,
            clan_data.category_id,
            boss_index,
            boss_status_data.lap,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_boss_status_data(clan_data: ClanData, boss_index: int):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_BOSS_STATUS_DATA_SQL, (
            clan_data.category_id,
            boss_index,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_all_boss_status_data(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_ALL_BOSS_STATUS_DATA_SQL, (
            clan_data.category_id,
        ))
        con.commit()
        con.close()

    @staticmethod
    def register_carryover_data(clan_data: ClanData, player_data: PlayerData, carryover: CarryOver):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(REGISTER_CARRYOVER_DATA_SQL, (
            clan_data.category_id,
            player_data.user_id,
            carryover.boss_index,
            carryover.attack_type.value,
            carryover.carry_over_time,
            carryover.created,
        ))
        con.commit()
        con.close()

    @staticmethod
    def update_carryover_data(clan_data: ClanData, player_data: PlayerData, carryover: CarryOver):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(UPDATE_CARRYOVER_DATA_SQL, (
            carryover.carry_over_time,
            clan_data.category_id,
            player_data.user_id,
            carryover.created,
        ))
        con.commit()
        con.close()
    
    @staticmethod
    def delete_carryover_data(clan_data: ClanData, player_data: PlayerData, carryover: CarryOver):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_CARRYOVER_DATA_SQL, (
            clan_data.category_id,
            player_data.user_id,
            carryover.created,
        ))
        con.commit()
        con.close()

    @staticmethod
    def reregister_carryover_data(clan_data: ClanData, player_data: PlayerData):
        """すでに登録してある持ち越しをすべて削除して登録しなおす"""
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_ALL_CARRYOVER_DATA_SQL, (
            clan_data.category_id,
            player_data.user_id,
        ))
        records = [(
            clan_data.category_id,
            player_data.user_id,
            carryover.boss_index,
            carryover.attack_type.value,
            carryover.carry_over_time,
            carryover.created
        ) for carryover in player_data.carry_over_list]
        cur.executemany(REGISTER_CARRYOVER_DATA_SQL, records)
        con.commit()
        con.close()

    @staticmethod
    def delete_all_carryover_data(clan_data: ClanData, plauer_data: PlayerData):
        """持ち越しのデータをすべて削除する"""
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute("delete from CarryOver where category_id=? and user_id=?", (
            clan_data.category_id,
            plauer_data.user_id,
        ))
        con.commit()
        con.close()

    @staticmethod
    def register_form_data(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(REGISTER_FORMDATA_SQL, (
            clan_data.category_id,
            clan_data.form_data.form_url,
            clan_data.form_data.sheet_url,
            clan_data.form_data.name_entry,
            clan_data.form_data.discord_id_entry,
            clan_data.form_data.created,
        ))
        con.commit()
        con.close()

    @staticmethod
    def update_form_data(clan_data: ClanData):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(UPDATE_FORMDATA_SQL, (
            clan_data.form_data.form_url,
            clan_data.form_data.sheet_url,
            clan_data.form_data.name_entry,
            clan_data.form_data.discord_id_entry,
            clan_data.form_data.created,
            clan_data.category_id,
        ))
        con.commit()
        con.close()

    @staticmethod
    def register_progress_message_id(clan_data: ClanData, lap: int):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        ids_list = clan_data.progress_message_ids[lap]
        cur.execute(REGISTER_PROGRESS_MESSAGEID_DATA, (
            clan_data.category_id,
            lap,
            ids_list[0],
            ids_list[1],
            ids_list[2],
            ids_list[3],
            ids_list[4],
        ))
        con.commit()
        con.close()

    @staticmethod
    def update_progress_message_id(clan_data: ClanData, lap: int):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        ids_list = clan_data.progress_message_ids[lap]
        cur.execute(UPDATE_PROGRESS_MESSAGEID_DATA, (
            ids_list[0],
            ids_list[1],
            ids_list[2],
            ids_list[3],
            ids_list[4],
            clan_data.category_id,
            lap,
        ))
        con.commit()
        con.close()

    @staticmethod
    def register_summary_message_id(clan_data: ClanData, lap: int):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        ids_list = clan_data.summary_message_ids[lap]
        cur.execute(REGISTER_SUMMARY_MESSAGEID_DATA, (
            clan_data.category_id,
            lap,
            ids_list[0],
            ids_list[1],
            ids_list[2],
            ids_list[3],
            ids_list[4],
        ))
        con.commit()
        con.close()

    @staticmethod
    def update_summary_message_id(clan_data: ClanData, lap: int):
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        ids_list = clan_data.summary_message_ids[lap]
        cur.execute(UPDATE_SUMMARY_MESSAGE_DATA, (
            ids_list[0],
            ids_list[1],
            ids_list[2],
            ids_list[3],
            ids_list[4],
            clan_data.category_id,
            lap,
        ))
        con.commit()
        con.close()

    @staticmethod
    def delete_old_data(clan_data: ClanData, lap: int):
        """日付更新時に古いデータを削除する"""
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        cur.execute(DELETE_OLD_BOSS_STATUS_DATA, (
            clan_data.category_id,
            lap,
        ))
        cur.execute(DELETE_OLD_ATTACK_STATUS_DATA, (
            clan_data.category_id,
            lap,
        ))
        cur.execute(DELETE_OLD_PROGRESS_MESSAGE_DATA, (
            clan_data.category_id,
            lap,
        ))
        cur.execute(DELETE_OLD_SUMMARY_MESSAGE_DATA, (
            clan_data.category_id,
            lap,
        ))
        con.commit()
        con.close()

    @staticmethod
    def load_clandata_dict() -> DefaultDict[int, ClanData]:
        clan_data_dict: DefaultDict[int, Optional[ClanData]] = defaultdict(lambda: None)
        con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = con.cursor()
        for row in cur.execute("select * from ClanData"):
            clan_data = ClanData(
                guild_id=row[0],
                category_id=row[1],
                boss_channel_ids=[row[2], row[3], row[4], row[5], row[6]],
                remain_attack_channel_id=row[7],
                reserve_channel_id=row[8],
                command_channel_id=row[9],
                summary_channel_id=row[16]
            )
            clan_data.reserve_message_ids = list(row[10:15])
            clan_data.remain_attack_message_id = row[15]
            clan_data.date = row[17]
            clan_data_dict[clan_data.category_id] = clan_data

        for row in cur.execute("select * from PlayerData"):
            player_data = PlayerData(row[1])
            player_data.physics_attack = row[2]
            player_data.magic_attack = row[3]
            player_data.task_kill = row[4]
            clan_data = clan_data_dict[row[0]]
            if clan_data:
                clan_data.player_data_dict[row[1]] = player_data

        for row in cur.execute("select * from ReserveData"):
            clan_data = clan_data_dict[row[0]]
            if not clan_data:
                continue
            player_data = clan_data.player_data_dict.get(row[2])
            if not player_data:
                continue
            reserve_data = ReserveData(
                player_data, ATTACK_TYPE_DICT[row[3]],
            )
            reserve_data.set_reserve_info((row[4], row[5], row[6]))
            clan_data.reserve_list[row[1]].append(reserve_data)

        for row in cur.execute("select * from BossStatusData"):
            clan_data = clan_data_dict[row[0]]
            if not clan_data:
                continue
            boss_status_data = BossStatusData(row[2], row[1])
            boss_status_data.beated = row[3]
            if boss_status_data.lap not in clan_data.boss_status_data.keys():
                clan_data.initialize_boss_status_data(boss_status_data.lap)
            clan_data.boss_status_data[boss_status_data.lap][row[1]] = boss_status_data

        for row in cur.execute("select * from AttackStatus"):
            clan_data = clan_data_dict[row[0]]
            if not clan_data:
                continue
            player_data = clan_data.player_data_dict.get(row[1])
            if not player_data:
                continue
            boss_status_data = clan_data.boss_status_data[row[2]][row[3]]
            attack_status = AttackStatus(
                player_data,
                ATTACK_TYPE_DICT[row[7]],
                row[8]
            )
            attack_status.damage = row[4]
            attack_status.memo = row[5]
            attack_status.attacked = row[6]
            attack_status.created = row[9].astimezone(JST)
            boss_status_data.attack_players.append(attack_status)

        for row in cur.execute("select * from CarryOver"):
            clan_data = clan_data_dict[row[0]]
            if not clan_data:
                continue
            player_data = clan_data.player_data_dict.get(row[1])
            if not player_data:
                continue
            carryover = CarryOver(ATTACK_TYPE_DICT[row[3]], row[2])
            carryover.carry_over_time = row[4]
            carryover.created = row[5].astimezone(JST)
            player_data.carry_over_list.append(carryover)

        for row in cur.execute("select * from FormData"):
            clan_data = clan_data_dict[row[0]]
            if not clan_data:
                continue
            clan_data.form_data.form_url = row[1]
            clan_data.form_data.sheet_url = row[2]
            clan_data.form_data.name_entry = row[3]
            clan_data.form_data.discord_id_entry = row[4]
            clan_data.form_data.created = row[5].astimezone(JST)

        for row in cur.execute("select * from ProgressMessageIdData"):
            if (clan_data := clan_data_dict[row[0]]) is None:
                continue
            clan_data.progress_message_ids[row[1]] = list(row[2:7])
        
        for row in cur.execute("select * from SummaryMessageIdData"):
            if (clan_data := clan_data_dict[row[0]]) is None:
                continue
            clan_data.summary_message_ids[row[1]] = list(row[2:7])
        
        con.close()
        return clan_data_dict
