import pymysql
from database_tool import DatabaseTool
import pandas as pd


def get_dataframe(value, description) -> pd.DataFrame:
    """
    transform sql query result to DataFrame
    :param tuple value:
    :param description:
    :return:
    """
    result = pd.DataFrame(value, columns=[x[0] for x in description])
    return result.groupby(level=0, axis=1).first()


class DatabaseOperate:
    __exercise_base = {"topic", "topic_picture", "answer", "answer_picture"}
    __exercise_extra = {"category", "chapter", "section", "difficulty"}

    def __init__(self, host, user, password, database):
        """
        connect the database by argus

        :param str host: database host
        :param str user: user name
        :param str password: user password
        :param str database: database name
        """
        self.__dbt = DatabaseTool(host, user, password, database)

    def add_exercise(self, topic, topic_picture, answer, answer_picture, category, chapter, part, difficulty):
        """
        add exercise to database

        :param str topic: describe of the exercise with ''
        :param str topic_picture: picture to supplement described
        :param str answer: answer of the exercise with ''
        :param str answer_picture: picture to supplement answer
        :param str category: category of the exercise with '' include '选择','填空','判断','名词解释','问答','算法','计算'
        :param int chapter: chapter of the exercise
        :param int part: part of the exercise
        :param str difficulty: difficulty of with the exercise with '' include '高','中','低'
        :return: None
        """
        tables = ["exercise_base_info", "exercise_extra_info"]
        columns = ["topic,topic_picture,answer,answer_picture", "category,chapter,part,difficulty"]
        values = [','.join([topic, topic_picture, answer, answer_picture]),
                  ','.join([category, str(chapter), str(part), difficulty])]
        self.__dbt.add(tables, columns, values)
        return self.__dbt.get_last_id()

    def add_paper(self, chapter, difficulty_high, difficulty_middle, difficulty_low):
        """
        add paper

        :param str chapter: range of paper
        :param double difficulty_high: percentage of high exercise
        :param double difficulty_middle: percentage of middle exercise
        :param double difficulty_low: percentage of low exercise
        :return:
        """
        tables = ["paper"]
        columns = ["chapter, difficulty_high, difficulty_middle, difficulty_low"]
        values = ["%s,%s,%s,%s" % (chapter, str(difficulty_high), str(difficulty_middle), str(difficulty_low))]
        self.__dbt.add(tables, columns, values)
        return self.__dbt.get_last_id()

    def test_exercise(self, test_id, exercise_id, point):
        """
        select exercise to test

        :param int test_id: the only representation of the paper
        :param int exercise_id: the only representation of the exercise
        :return:
        """
        tables = ["paper_exercise"]
        columns = ["MAX(number)"]
        conditions = ["where TestCode=%s" % test_id]
        num = self.__dbt.query(tables, columns, conditions).iat[0, 0]
        if num is None:
            num = 1
        else:
            num += 1
        columns = ["TestCode, ExerciseCode, number, point"]
        values = ["%d,%d,%d,%s" % (test_id, exercise_id, num, str(point))]
        self.__dbt.add(tables, columns, values)

    def delete_exercise(self, exercise_id):
        """
        delete the exercise from database by exercise id

        :param int exercise_id: the only representation of the exercise
        :return:
        """
        tables = ["exercise_base_info"]
        conditions = ["ExerciseCode = %d" % exercise_id]
        self.__dbt.delete(tables, conditions)

    def delete_paper(self, test_id):
        """
        delete the paper from database by test id

        :param int test_id: the only representation of the paper
        :return:
        """
        tables = ["paper"]
        conditions = ["TestCode = %d" % test_id]
        self.__dbt.delete(tables, conditions)

    def update_exercise(self, exercise_id, columns, values):
        """
        update exercise by argus


        :param int exercise_id: the only representation of the exercise
        :param columns: the all index of the update values
        :param values: all update value
        :return:
        """
        pretreatment = dict(zip(columns, values))
        update_base = []
        update_extra = []
        tables = []
        conditions = []
        for key, value in pretreatment.items():
            if key in self.__exercise_base:
                update_base += [key + '=' + value]
                if "exercise_base_info" not in tables:
                    tables.append("exercise_base_info")
                conditions.append("ExerciseCode=%d" % exercise_id)
            if key in self.__exercise_extra:
                update_extra += [key + '=' + value]
                if "exercise_extra_info" not in tables:
                    tables.append("exercise_extra_info")
                conditions.append("ExerciseCode=%d" % exercise_id)

        content = [','.join(update_base), ','.join(update_extra)]
        self.__dbt.update(tables, content, conditions)

    def query_exercise(self, condition) -> pd.DataFrame:
        """
        query exercise from database by condition.
        condition="all" means query all exercise

        :param str condition: query by condition
        :return:
        """
        if condition == "all":
            condition = ''
        else:
            condition = "where %s" % condition

        base = "exercise_base_info"
        extra = "exercise_extra_info"

        tables = ["%s join %s on %s.ExerciseCode=%s.ExerciseCode" % (base, extra, base, extra)]
        columns = ["*"]
        conditions = [condition]
        return self.__dbt.query(tables, columns, conditions)

    def query_extra_exercise(self, condition) -> pd.DataFrame:
        """
        query exercise from database by condition.
        condition="all" means query all exercise

        :param str condition: query by condition
        :return:
        """
        if condition == "all":
            condition = ''
        else:
            condition = "where %s" % condition

        tables = ["exercise_extra_info"]
        columns = ["*"]
        conditions = [condition]
        return self.__dbt.query(tables, columns, conditions)

    def query_paper(self, condition) -> pd.DataFrame:
        """
        query paper from database by condition.
        condition="all" means query all paper

        :param str condition: query by condition
        :return:
        """
        if condition == "all":
            condition = ''
        else:
            condition = "where %s" % condition

        tables = ["paper"]
        columns = ["*"]
        conditions = [condition]
        return self.__dbt.query(tables, columns, conditions)

    def query_exercise_from_paper(self, test_id):
        tables = ["paper_exercise"]
        columns = ["*"]
        conditions = ["where TestCode=%d" % test_id]
        return self.__dbt.query(tables,columns,conditions)

    def statistic_exercise(self, column) -> pd.DataFrame:
        """
        Statistics the num of exercise
        :param str column: Statistics by this column
        :return:
        """
        tables = []
        if column in self.__exercise_base:
            tables = ["exercise_base_info"]
        if column in self.__exercise_extra:
            tables = ["exercise_extra_info"]
        columns = ["%s, COUNT(ExerciseCode) as num" % column]
        conditions = ["group by %s" % column]
        return self.__dbt.query(tables, columns, conditions)


def main():
    pd.set_option('display.max_columns', None,
                  'display.max_rows', None,
                  'display.max_colwidth', None,
                  'display.width', 100,
                  'expand_frame_repr', False)
    opr = DatabaseOperate("104.168.172.47", "forfind", "000000", "exercise")
    opr.test_exercise(1,170,2)
    ques_data = opr.query_exercise_from_paper(1)
    print(ques_data)

    '''
    add = opr.add_paper("'1,2,3'",0.1,0.8,0.1)
    print(add)
    paper = opr.query_paper("all")
    print(paper)
    '''

    '''
    for chap in [1,2,3,4,5,7]:
        for category in ["'名词解释'","'问答'","'算法'","'计算'"]:
            for diff in ["'低'","'高'","'中'"]:
                for i in range(10):
                    print(chap,category,diff,i)
                    opr.add_exercise("'"+"测试用例|"+diff[1:-1]+"|CHAP"+str(chap)+"|"+category[1:-1]+"|ques"+str(i)+"'", "null", "'ans"+str(i)+"'", "null", category, chap, i, diff)
    '''

if __name__ == '__main__':
    main()
