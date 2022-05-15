benjamin/data_store: I assumed that the functionality of the function Datastore in data_store.py would not be affected by the altering of the structure of initial_object, as l am not changing its type from dictionary. ie i assumed it unnecessary to test.

benjamin/clear_v1: I assumed that as we are not implementing messages yet, it would not be possible to black box test that clear_v1() is able to clear messages in data_store. I also assumed that it is not necessary to clear messages yet, as they are not stored to begin with.
