def add_new_items(str_1:str, str_2:str, n:int=6):
        list_1 = str_1.splitlines()
        list_2 = str_2.splitlines()
        if list_1 == list_2:
            return True, list_1 # this is for the first adding.
        # Determine the comparison range: use all of list_1 if it's shorter than list_2
        comparison_range = list_1[-len(list_2):] if len(list_1) >= len(list_2) else list_1
        # Check if list_2 is already included in list_1
        if all(item in list_1 for item in list_2):
            return False  # If all items in list_2 are already in list_1, return False
        # Advanced mode: check if the first `n` items match between the end of list_1 and the start of list_2
        consecutive_match = True
        for i in range(min(n, len(list_1), len(list_2))):  # Limit to the shortest list or `n`
            if list_1[-(i+1)] != list_2[-(i+1)]:
                consecutive_match = False
                break
        # Flag to indicate if something was added
        added = False
        # If advanced mode conditions are met (n consecutive items match), append the rest of list_2
        if consecutive_match and len(list_1) >= n:
            list_1.extend(list_2[n:])
            added = True
        else:
            # Fall back to single-item comparison mode
            for item in list_2:
                if item not in comparison_range:
                    list_1.append(item)
                    added = True
        return added, '\n'.join(list_1)  # Return True if something was added, False otherwise

if __name__ == "__main__":
    list_1 = "1\n2\n3\n4\n5\n6\n7\n8\n9\n10"
    list_2 = " "
    added, list_1 = add_new_items(list_1, list_2)
    print(added, list_1)