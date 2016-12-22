def calculate_box(matrix):
    """return the buffer of integral image technique

    :param matrix: 2-D array
    :return: 2-D calculated buffer
    """
    height, width = len(matrix), len(matrix[0])
    buff = matrix[0][:]
    res = [buff[:]]
    for i in range(1, height):
        row_res = []
        for j in range(width):
            buff[j] += matrix[i][j]
            tmp = buff[j] if j == 0 else row_res[j-1] + buff[j]
            row_res.append(tmp)
        res.append(row_res)
    return res


# calculate the sum of the box in the matrix:
# --------------------------------
# - pos_lu  pixel  pixel  pos_ru -
# - pixel   pixel  pixel  pixel  -
# - pos_lb  pixel  pixel  pos_rb -
# --------------------------------
# params are tuples (x, y)
def calculate_sum(matrix, pos_lu, pos_ru, pos_lb, pos_rb):
    total = matrix[pos_rb[0]][pos_rb[1]]

    pass


def array_multiply(m1, m2):
    """array multiply: m1 * m2, m1 and m2 should share the same size

    :param m1: 2-D array
    :param m2: 2-D array
    :return: m1 * m2
    """
    res = []
    for row1, row2 in list(zip(m1, m2)):
        l = len(row1)
        res.append([row1[i] * row2[i] for i in range(l)])
    return res


def list_to_matrix(l, w, h):
    res = []
    for i in range(h):
        res.append(l[i * w:i * w + w])
    return res


def matrix_to_list(mat):
    res = []
    for row in mat:
        for ele in row:
            res.append(ele)
    return res


def padding(mat, padding_num):
    """

    :param mat: source matrix to be padded
    :param padding_num:  padding number
    :return: matrix after 0-padding
    """
    new_mat = []
    m, n = len(mat), len(mat[0])
    for i in range(padding_num * 2 + m):
        new_mat.append([0 for j in range(padding_num * 2 + n)])
    cur_x, cur_y = padding_num, padding_num
    for row in mat:
        for ele in row:
            new_mat[cur_x][cur_y] = ele
            cur_y += 1
        cur_y = padding_num
        cur_x += 1
    return new_mat
