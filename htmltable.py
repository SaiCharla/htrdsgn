#!vim: fileencoding=utf-8
# Author: SaiCharla

import html

def htable(header, body):
    """Returns a html formatted table"""
    style = """<style>
            table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }

            td, th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }

            tr:nth-child(even) {
                background-color: #dddddd;
            }
            </style>"""
    table = """<h2>Possible Heaters</h2>
               <table>
                {0}
               <\table>"""
    hl = "<th>{0}</th>"
    tr = "<tr>{0}</tr>"
    td = "<td>{0}</td>"
    heading = hl.format(tr.format(''.join([td.format(h) for h in
        header.split('\t')])))
    rowlist = []
    for line in body:
        rowlist.append(tr.format(''.join([td.format(word) for word in
            line.split('\t')])))
    return html.unescape(style+table.format(heading+''.join(rowlist)))
