import pandas as pd
import ttg  # https://github.com/chicolucio/truth-table-generator
import numpy as np
from IPython.display import Markdown
import json


class KarnaughMap:
    def __init__(self, row_vars, col_vars):
        self.row_vars = row_vars
        self.col_vars = col_vars
        self.kmap = None
        self.computeMap()

    def __repr__(self):
        display(self.kmap)
        return ""

    def computeMap(self):
        self.kmap = pd.concat(
            [
                pd.DataFrame(
                    np.zeros(
                        [2**len(self.row_vars), 2**len(self.col_vars)], dtype=int
                    ),
                    index=self.computeIndice(self.row_vars),
                    columns=self.computeIndice(self.col_vars),
                )
            ],
            axis=1,
        )
        return self.kmap

    def computeIndice(self, list_of_vars):
        v_len = len(list_of_vars)
        v = list_of_vars
        v += [None for x in range(v_len)]

        binary_switcher = {
            1: ["0", "1"],
            2: ["00", "01", "11", "10"],
            3: ["000", "001", "011", "010", "110", "111", "101", "100"],
            # 3: ["000", "001", "011", "010", "100","101","111","110"],
        }
        algebraic_switcher = {
            1: [f"{v[0]}'", f"{v[0]}"],
            2: [f"{v[0]}'{v[1]}'", f"{v[0]}'{v[1]}", f"{v[0]}{v[1]}", f"{v[0]}{v[1]}'"],
            3: [
                f"{v[0]}'{v[1]}'{v[2]}'",
                f"{v[0]}'{v[1]}'{v[2]}",
                f"{v[0]}'{v[1]}{v[2]}",
                f"{v[0]}'{v[1]}{v[2]}'",
                f"{v[0]}{v[1]}{v[2]}'",
                f"{v[0]}{v[1]}{v[2]}",
                f"{v[0]}{v[1]}'{v[2]}",
                f"{v[0]}{v[1]}'{v[2]}'",
            ],
            # 3: [
            #     f"{v[0]}'{v[1]}'{v[2]}'",
            #     f"{v[0]}'{v[1]}'{v[2]}",
            #     f"{v[0]}'{v[1]}{v[2]}",
            #     f"{v[0]}'{v[1]}{v[2]}'",
            #     f"{v[0]}{v[1]}'{v[2]}",
            #     f"{v[0]}{v[1]}'{v[2]}'",
            #     f"{v[0]}{v[1]}{v[2]}'",
            #     f"{v[0]}{v[1]}{v[2]}'",
            # ],
            
        }
        # display(zip(binary_switcher.get(v_len), algebraic_switcher.get(v_len) ))
        # display(binary_switcher.get(v_len), algebraic_switcher.get(v_len))

        index = pd.MultiIndex.from_tuples(
            [
                (state, algebraic)
                for state, algebraic in zip(
                    binary_switcher.get(v_len), algebraic_switcher.get(v_len)
                )
            ]
        )
        return index

    def getIndices(self, column_vars, indice_vars):
        ab, cd = self.computeIndice(column_vars), self.computeIndice(indice_vars)
        return ab, cd


class PiTable:
    def __init__(self, prime_implicants, fn):
        self.prime_implicants = prime_implicants
        self.fn = fn
        self.data = np.zeros([len(self.prime_implicants), len(self.fn)], dtype=int)
        self.pt = self.computeTable()
        pass

    def __repr__(self):
        self.computeTable()
        display(self.pt)
        return "PI Table"

    def computeTable(self):
        idx = pd.MultiIndex.from_tuples(
            [(cols, algebraic) for cols, algebraic in self.prime_implicants]
        )
        self.pt = pd.DataFrame(self.data, index=idx, columns=[self.fn])

        for i, row in enumerate(idx):
            for j in json.loads(row[0]):
                if j != 'x':
                    self.pt.iloc[i][j] = 1
                pass
        return self.pt

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data


class Solver:
    def __init__(self, num_vars=None, fn=None, expression=None, show_legend=False):
        self.truthtable = None
        self.kmap = None
        self.kmap_legend = None
        self.num_vars = None
        self.vars = None
        self.km_rows = None
        self.km_cols = None
        self.expression = None

        if num_vars is not None:
            self.num_vars = num_vars
            v_switcher = {
                2: ["A", "B"],
                3: ["A", "B", "C"],
                4: ["A", "B", "C", "D"],
                5: ["A", "B", "C", "D", "E"],
            }
            km_switcher = {
                2: [["A"], ["B"]],
                3: [["A", "B"], ["C"]],
                4: [["A", "B"], ["C", "D"]],
                5: [["A", "B", "C"], ["D", "E"]],
            }
            self.vars = v_switcher.get(num_vars)
            self.km_rows, self.km_cols = km_switcher.get(num_vars)
            self.kmap = KarnaughMap(self.km_rows.copy(), self.km_cols.copy())
            self.truthtable = self.tt(self.vars)
        if fn is not None:
            self.truthtable = pd.concat(
                [self.tt(self.vars), pd.DataFrame({"F": fn})], axis=1
            )
            self.truthTableToKmap(show_legend)
            pass
        if expression is not None:
            self.truthtable = self.tt(self.vars, expression)
            self.truthtable = self.truthtable.rename(columns={expression[0]: "F"})
            self.truthTableToKmap(show_legend)
            pass

    def display(self, kmap=True, truth_table=True):
        display(Markdown("### Truth Table"))
        display(self.truthtable if truth_table else None)
        display(Markdown("### KMAP"))
        display(self.kmap if kmap else None)
        display(Markdown("### KMAP Legend"))
        self.truthTableToKmap(True)
        display(self.kmap if kmap else None)

    # TODO save kmap legend to a different member variable
    def truthTableToKmap(self, legend=False):
        for i, x in enumerate(self.truthtable.index):
            r = self.truthtable.iloc[i]
            rv = i if (legend is True) else r["F"]
            if self.num_vars == 2:
                self.kmap.kmap.loc[[f"{r['A']}"], [f"{r['B']}"]] = rv
            if self.num_vars == 3:
                self.kmap.kmap.loc[[f"{r['A']}{r['B']}"], [f"{r['C']}"]] = rv
            if self.num_vars == 4:
                self.kmap.kmap.loc[[f"{r['A']}{r['B']}"], [f"{r['C']}{r['D']}"]] = rv
            if self.num_vars == 5:
                self.kmap.kmap.loc[[f"{r['A']}{r['B']}{r['C']}"], [f"{r['D']}{r['E']}"]] = rv

    def tt(self, args_list, exprs=None):
        df = (ttg.Truths(args_list, exprs).as_pandas())[::-1]
        df = df.reset_index(drop=True)
        return df
