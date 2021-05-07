#coding:utf-8
"""
Created on Tue Mar 26 21:16:49 2019

@author: jiali zhang

bearing fault diagnosis by cnn
"""
import os
import tensorflow.keras
from tensorflow.keras.layers import Dense, Conv1D, BatchNormalization, MaxPooling1D, Activation, Flatten, Dropout, LSTM
from tensorflow.keras.utils import plot_model
from tensorflow.keras.regularizers import l2
import preprocess
import numpy as np
import time

os.environ["PATH"] += os.pathsep + 'D:/Graphviz/bin/'  #注意修改你的路径
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# 训练参数
batch_size = 128
epochs = 15
num_classes = 10
length = 2048
BatchNorm = True # 是否批量归一化
number = 1000 # 每类样本的数量
normal = True # 是否标准化
rate = [0.7,0.2,0.1] # 测试集验证集划分比例
mark=time.strftime("%Y%m%d_%H%M", time.localtime())

path = r'data\0HP'
x_train, y_train, x_valid, y_valid, x_test, y_test = preprocess.prepro(d_path=path,length=length,
                                                                  number=number,
                                                                  normal=normal,
                                                                  rate=rate,
                                                                  enc=True, enc_step=28)

x_train, x_valid, x_test = x_train[:,:,np.newaxis], x_valid[:,:,np.newaxis], x_test[:,:,np.newaxis]

input_shape =x_train.shape[1:]

print('训练样本维度:', x_train.shape)
print(x_train.shape[0], '训练样本个数')
print('验证样本的维度', x_valid.shape)
print(x_valid.shape[0], '验证样本个数')
print('测试样本的维度', x_test.shape)
print(x_test.shape[0], '测试样本个数')


model_name = "cnn_diagnosis-{}".format(mark)

# 实例化一个Sequential
model = tensorflow.keras.models.Sequential()

#第一层卷积
model.add(Conv1D(filters=16, kernel_size=64, strides=16, padding='same', kernel_regularizer=l2(1e-4), input_shape=input_shape))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling1D(pool_size=2))

#第二层卷积
model.add(Conv1D(32,kernel_size=3, strides=1, padding='same', kernel_regularizer=l2(1e-4), input_shape=input_shape))
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling1D(pool_size=2, strides=2, padding='valid'))

#LSTM层
#model.add(LSTM(64, activation='tanh', recurrent_activation='hard_sigmoid', kernel_initializer='glorot_uniform', recurrent_initializer='orthogonal', bias_initializer='zeros', return_sequences=True))

# 从卷积到全连接需要展平
model.add(Flatten())
model.add(Dropout(0.2))

# 添加全连接层
model.add(Dense(32))
model.add(Activation("relu"))

# 增加输出层，共num_classes个单元
model.add(Dense(units=num_classes, activation='softmax', kernel_regularizer=l2(1e-4)))


# 编译模型
model.compile(optimizer='Adam', loss='categorical_crossentropy',
              metrics=['accuracy'])

# TensorBoard调用查看一下训练情况
logdir = os.path.join('logs','date', model_name)
tb_cb = tensorflow.keras.callbacks.TensorBoard(log_dir=logdir)
# tb_cb = tensorflow.keras.callbacks.TensorBoard(log_dir='logs/{}_logs/{}'.format('date', model_name))

# 开始模型训练
model.fit(x=x_train, y=y_train, batch_size=batch_size, epochs=epochs,
          verbose=1, validation_data=(x_valid, y_valid), shuffle=True,
          callbacks=[tb_cb])

# 评估模型
score = model.evaluate(x=x_test, y=y_test, verbose=0)
print("测试集上的损失率：", score[0])
print("测试集上的准确率：", score[1])
plot_model(model=model, to_file='images/cnn-diagnosis.png', show_shapes=True)
