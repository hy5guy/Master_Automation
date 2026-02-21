// 🕒 2026-02-20-23-48-50
// # patrol/___Patrol.m
// # Author: R. A. Carucci
// # Purpose: Load Patrol Division monthly activity metrics with wide-format month columns.

let
    Source = Excel.Workbook(File.Contents("C:\Users\carucci_r\OneDrive - City of Hackensack\Shared Folder\Compstat\Contributions\Patrol\patrol_monthly.xlsm"), null, true),
    _mom_patrol_Table = Source{[Item="_mom_patrol",Kind="Table"]}[Data],
#"Changed Type" = Table.TransformColumnTypes(                                  \
    _mom_patrol_Table, {{"Tracked Items", type text },                         \
                         {"06-23", Int64.Type },                               \
                          {"07-23", Int64.Type },                              \
                           {"08-23", Int64.Type },                             \
                            {"09-23", Int64.Type },                            \
                             {"10-23", Int64.Type },                           \
                              {"11-23", Int64.Type },                          \
                               {"12-23", Int64.Type },                         \
                                {"01-24", Int64.Type },                        \
                                 {"02-24", Int64.Type },                       \
                                  {"03-24", Int64.Type },                      \
                                   {"04-24", Int64.Type },                     \
                                    {"05-24", Int64.Type },                    \
                                     {"06-24", Int64.Type },                   \
                                      {"07-24", Int64.Type },                  \
                                       {"08-24", Int64.Type },                 \
                                        {"09-24", Int64.Type },                \
                                         {"10-24", Int64.Type },               \
                                          {"11-24", Int64.Type },              \
                                           {"12-24", Int64.Type },             \
                                            {"01-25", Int64.Type },            \
                                             {"02-25", Int64.Type },           \
                                              {"03-25", Int64.Type },          \
                                               {"04-25", Int64.Type },         \
                                                {"05-25", Int64.Type },        \
                                                 {"06-25", Int64.Type },       \
                                                  {"07-25", Int64.Type },      \
                                                   {"08-25", Int64.Type },     \
                                                    {"09-25", Int64.Type },    \
                                                     {"10-25", Int64.Type },   \
                                                      {"11-25", Int64.Type },  \
                                                       {"12-25",               \
                                                        Int64.Type } })
in
#"Changed Type"
