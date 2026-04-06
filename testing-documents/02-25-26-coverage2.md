```shell
============================= test session starts ==============================
platform darwin -- Python 3.12.12, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/txlon5/Downloads/COSC310_TermProject_Group21
plugins: anyio-4.12.1, cov-7.1.0
collected 212 items

backend/test/test_auth.py ..........                                     [  4%]
backend/test/test_get_order_by_id.py .                                   [  5%]
backend/test/test_main.py .                                              [  5%]
backend/test/test_menu_api.py .........                                  [  9%]
backend/test/test_menu_service.py .............                          [ 16%]
backend/test/test_notification_sr1.py .....                              [ 18%]
backend/test/test_notification_sr2.py ....                               [ 20%]
backend/test/test_notification_sr3.py ...                                [ 21%]
backend/test/test_order_cost_sr1.py ......                               [ 24%]
backend/test/test_order_cost_sr2.py ........                             [ 28%]
backend/test/test_order_feat5_us3.py .                                   [ 28%]
backend/test/test_order_status_feat5.py ....                             [ 30%]
backend/test/test_orders_api.py ..                                       [ 31%]
backend/test/test_orders_repository.py ......                            [ 34%]
backend/test/test_orders_service.py ....................                 [ 43%]
backend/test/test_past_order_history_sr1.py ..                           [ 44%]
backend/test/test_past_order_history_sr2.py ....                         [ 46%]
backend/test/test_past_order_history_sr3.py ....                         [ 48%]
backend/test/test_payment_methods.py ..........................          [ 60%]
backend/test/test_payment_transactions.py .....................          [ 70%]
backend/test/test_restaurants_api.py ...                                 [ 72%]
backend/test/test_restaurants_feat2_sr1.py ....                          [ 74%]
backend/test/test_restaurants_repository.py ..                           [ 75%]
backend/test/test_restaurants_service.py .......................         [ 85%]
backend/test/test_sr1_order_fields.py ..                                 [ 86%]
backend/test/test_users.py .......................                       [ 97%]
backend/test/test_users_unauthorized.py .....                            [100%]

================================ tests coverage ================================
______________ coverage: platform darwin, python 3.12.12-final-0 _______________

Name                                                     Stmts   Miss Branch BrPart  Cover
------------------------------------------------------------------------------------------
backend/app/__init__.py                                      0      0      0      0   100%
backend/app/auth/__init__.py                                 0      0      0      0   100%
backend/app/auth/password_utils.py                           8      0      0      0   100%
backend/app/auth/token_utils.py                             27      0      2      0   100%
backend/app/main.py                                         24      0      0      0   100%
backend/app/repositories/__init__.py                         0      0      0      0   100%
backend/app/repositories/orders_repository.py               16      0      2      0   100%
backend/app/repositories/payment_methods_repository.py      14      1      2      1    88%
backend/app/repositories/restaurants_repository.py          19      0      4      0   100%
backend/app/repositories/transactions_repository.py         14      1      2      1    88%
backend/app/repositories/users_repo.py                      14      1      2      1    88%
backend/app/routers/__init__.py                              0      0      0      0   100%
backend/app/routers/auth.py                                 11      0      0      0   100%
backend/app/routers/menus.py                                19      0      0      0   100%
backend/app/routers/notifications.py                         9      0      0      0   100%
backend/app/routers/order_cost.py                           13      0      0      0   100%
backend/app/routers/orders.py                               31      1      2      0    97%
backend/app/routers/payment_methods.py                      26      0      2      0   100%
backend/app/routers/restaurants_router.py                   27      2      0      0    93%
backend/app/routers/transactions_router.py                  29      3      6      3    83%
backend/app/routers/users.py                                45      0     10      0   100%
backend/app/schemas/__init__.py                              0      0      0      0   100%
backend/app/schemas/auth.py                                  5      0      0      0   100%
backend/app/schemas/card_validator.py                       22      0      0      0   100%
backend/app/schemas/delivery.py                             12      0      0      0   100%
backend/app/schemas/item.py                                  4      0      0      0   100%
backend/app/schemas/menu.py                                 21      0      0      0   100%
backend/app/schemas/notification.py                          9      0      0      0   100%
backend/app/schemas/order.py                                68      0      0      0   100%
backend/app/schemas/order_cost.py                           28      1      2      1    93%
backend/app/schemas/payment_method.py                       22      0      0      0   100%
backend/app/schemas/payment_transaction.py                  27      0      0      0   100%
backend/app/schemas/restaurant.py                           22      0      0      0   100%
backend/app/schemas/user.py                                 16      0      0      0   100%
backend/app/schemas/user_validator.py                       26      1      8      1    94%
backend/app/services/__init__.py                             0      0      0      0   100%
backend/app/services/menu_service.py                        95      4     42      6    93%
backend/app/services/notification_service.py                19      0      0      0   100%
backend/app/services/order_cost_service.py                  49      2     18      2    94%
backend/app/services/orders_service.py                     123      2     58      7    95%
backend/app/services/payments_service.py                   182      5    102     13    94%
backend/app/services/restaurants_service.py                 87      0     40      3    98%
backend/app/services/users_service.py                       82      3     42      3    95%
backend/test/__init__.py                                     0      0      0      0   100%
backend/test/conftest.py                                    17      0      0      0   100%
backend/test/test_auth.py                                   51      0      0      0   100%
backend/test/test_get_order_by_id.py                        37      0      0      0   100%
backend/test/test_main.py                                    7      0      0      0   100%
backend/test/test_menu_api.py                               81      0      0      0   100%
backend/test/test_menu_service.py                           71      0      0      0   100%
backend/test/test_notification_sr1.py                       72      0      0      0   100%
backend/test/test_notification_sr2.py                       75      0      0      0   100%
backend/test/test_notification_sr3.py                       74      0      0      0   100%
backend/test/test_order_cost_sr1.py                         34      0      0      0   100%
backend/test/test_order_cost_sr2.py                         58      0      0      0   100%
backend/test/test_order_feat5_us3.py                        19      0      0      0   100%
backend/test/test_order_status_feat5.py                     43      1      0      0    98%
backend/test/test_orders_api.py                             40      0      0      0   100%
backend/test/test_orders_repository.py                      84      0      2      0   100%
backend/test/test_orders_service.py                        144      1      0      0    99%
backend/test/test_past_order_history_sr1.py                 67      0      2      0   100%
backend/test/test_past_order_history_sr2.py                 79      0      0      0   100%
backend/test/test_past_order_history_sr3.py                 63      0      0      0   100%
backend/test/test_payment_methods.py                       179      1      0      0    99%
backend/test/test_payment_transactions.py                  185      5      0      0    97%
backend/test/test_restaurants_api.py                        14      0      0      0   100%
backend/test/test_restaurants_feat2_sr1.py                  41      0      0      0   100%
backend/test/test_restaurants_repository.py                 12      0      0      0   100%
backend/test/test_restaurants_service.py                   167      0      0      0   100%
backend/test/test_sr1_order_fields.py                       19      0      0      0   100%
backend/test/test_users.py                                 147      0      0      0   100%
backend/test/test_users_unauthorized.py                     30      0      0      0   100%
------------------------------------------------------------------------------------------
TOTAL                                                     3175     35    350     42    98%
============================= 212 passed in 2.20s ==============================
Finished running tests!

```
