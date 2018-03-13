import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf

def read_data(filename,row_start = 0,row_end = None,column_start = 0, column_end = None,print_shape = True):
    rawdata = np.array(pd.read_csv(filename))
    if(row_end == None):
        rawdata = rawdata[row_start:,:]
    else:
        rawdata = rawdata[row_start:row_end,:]
    if(column_start == None):
        rawdata = rawdata[:,column_start:];
    else:
        rawdata = rawdata[:,column_start:column_end];
    if(print_shape):
        print(rawdata.shape);
    rawdata[:,2] = -(rawdata[:,2]+180)
    rawdata[:,3] = -(rawdata[:,3])
    return rawdata

def single_line_visualize(Column,label = 'Angle1',color = 'b',line_type = 'o',markersize = 1):
    plt.figure(22,figsize = (18,5.4))
    plt.plot(pd.Series(Column),color+line_type,markersize = markersize,label = label)
    plt.legend(loc = 'upper left')
    plt.show()


def main_visualize(data,start,end,color = 'b',line_type = 'o',markersize = 1):
    picnum = 6
    plt.figure(22,figsize = (18,picnum*5.4))

    plt.subplot(611)
    plt.plot(pd.Series((data[start:end,0])),color + line_type,markersize = markersize,label = 'Angle1')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(612)
    plt.plot(pd.Series((data[start:end,2])),color + line_type,markersize = markersize,label = 'Angle2')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(613)
    plt.plot(pd.Series((data[start:end,0] - data[start:end,2])),color + line_type,markersize = markersize,label = 'A1 - A2')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(614)
    plt.plot(pd.Series((data[start:end,4])),color + line_type,markersize = markersize,label = 'spike1')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(615)
    plt.plot(pd.Series((data[start:end,5])),color + line_type,markersize = markersize,label = 'spike2')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(616)
    plt.plot(pd.Series((data[start:end,6])),color + line_type,markersize = markersize,label = 'spike3')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.show()


def print_info(data):
    for i in range(7):
        if(i==0):
            print('angle1')
        if(i==1):
            print('omega1')
        if(i==2):
            print('angle2')
        if(i==3):
            print('omega2')
        if(i>3):
            print('spike',i-3)
        print('mean:,',data[:,i].mean())
        print('std:,',data[:,i].std())

def print_y_info(data_dict):
    for i in range(1,5):
        print('y',i)
        print(data_dict['truey' + str(i)].mean())
        print(data_dict['truey' + str(i)].std())

def build_Angle_RNN_cells(hidden_angle):
    cells = [];
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units =hidden_angle,
                                             activation = tf.nn.relu
                                             ))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units =hidden_angle,
                                             activation = tf.nn.relu
                                             ))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units =hidden_angle,
                                             activation = tf.nn.relu
                                             ))
    cells = tf.contrib.rnn.MultiRNNCell(cells)
    return cells

def build_Emg_RNN_cells(hidden_emg):

    cell_emg =[];
    cell_emg.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden_emg,
                                                activation = tf.nn.relu
                                                ))
    cell_emg.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden_emg,
                                                activation = tf.nn.relu
                                                ))
    cell_emg = tf.contrib.rnn.MultiRNNCell(cell_emg)
    return cell_emg
def train_model(data_dict,is_new,ckptname,learning_rate,beta,epochs,ration,cluster_num,filenum,saver_name = None):
    if(saver_name == None):
        saver_name = ckptname
    input_angle = 4
    input_emg = 3
    outputshape = 1
    num_periods = 1080

    hidden_angle = 25
    hidden_emg = 15

    output2 = 25
    output3 = 15

    tf.reset_default_graph()
    
    x_angle = tf.placeholder(tf.float32,[None,1080,input_angle])
    x_emg = tf.placeholder(tf.float32,[None,1080,input_emg])
    y = tf.placeholder(tf.float32,[None,1080,outputshape]);
    
    cells = build_Angle_RNN_cells(hidden_angle)
    cell_emg = build_Emg_RNN_cells(hidden_emg)

    rnn_output,states = tf.nn.dynamic_rnn(cells,x_angle,
                                          dtype = tf.float32,
                                          scope = 'cells')
    emg_output,emg_states = tf.nn.dynamic_rnn(cell_emg,x_emg,
                                              dtype = tf.float32,
                                              scope = 'cell_emg')

    stacked_rnn_output = tf.reshape(rnn_output,[-1,hidden_angle])
    stacked_emg_output = tf.reshape(emg_output,[-1,hidden_emg])

    concat = tf.concat([stacked_rnn_output,stacked_emg_output],1)

    stacked_output = tf.layers.dense(concat,output2,name = 'dense')
    hidden_dense = tf.layers.dense(tf.nn.relu(stacked_output),
                                   output3,name = 'hidden_dense')
    output = tf.layers.dense(tf.nn.relu(hidden_dense),
                             outputshape,name = 'dense2')
    outputs = tf.reshape(output,[-1,num_periods,outputshape])

    MSE = tf.reduce_mean(tf.square(outputs[:,10:] - y[:,10:]))

    Qua = tf.reduce_mean(tf.square(tf.square(
                            outputs[:,10:] - y[:,10:]
                                       ) ) )

    Regulizer = beta*(tf.nn.l2_loss(tf.trainable_variables('cells')[0])+
                      tf.nn.l2_loss(tf.trainable_variables('cells')[2])+
                      tf.nn.l2_loss(tf.trainable_variables('cells')[4])+
                      tf.nn.l2_loss(tf.trainable_variables('dense')[0])+
                      tf.nn.l2_loss(tf.trainable_variables('hidden_dense')[0])+
                      tf.nn.l2_loss(tf.trainable_variables('dense2')[0])+
                      0.01*tf.nn.l2_loss(tf.trainable_variables('cell_emg')[0])+
                      0.01*tf.nn.l2_loss(tf.trainable_variables('cell_emg')[2])
                      )
    loss = tf.add(tf.add(Qua,Regulizer),ration*MSE)
    optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
    gvs = optimizer.compute_gradients(loss)
    capped_gvs = [(tf.clip_by_value(grad,-2,2),var) for grad,var in gvs]
    training_op = optimizer.apply_gradients(capped_gvs)
    init = tf.global_variables_initializer()
    mse = 0
    List1 = []
    data_angle = np.zeros((cluster_num,num_periods,input_angle))
    data_emg = np.zeros((cluster_num,num_periods,input_emg))
    y_data = np.zeros((cluster_num,num_periods,outputshape))

    for i in range(1,2*filenum + 1):
        List1.append(data_dict['datax' + str(i)].shape[0] - num_periods)
    with tf.Session() as sess:
        if(is_new):
            init.run()
        else:
            saver = tf.train.Saver()
            checkpoint_filepath = 'ckptset\\' + ckptname
            saver.restore(sess,checkpoint_filepath)
            term = 0
            for ep in range(epochs):
                source = np.random.randint(1,2*filenum + 1,cluster_num,dtype = int)
                for i in range(cluster_num):
                    index = np.random.randint(0,List1[source[i]-1])
                    data_angle[i,:,:] = data_dict['datax' + str(source[i])][index:index+num_periods,0:4]
                    data_emg[i,:,:] = data_dict['datax' + str(source[i])][index:index+num_periods,4:7]
                    y_data[i,:,:] = data_dict['datay' + str(source[i])][index:index+num_periods,:]
                sess.run(training_op,feed_dict = { x_angle:data_angle,x_emg:data_emg,y:y_data})
                if ep%10 == 0:
                    mse +=MSE.eval(feed_dict = {x_angle:data_angle,x_emg:data_emg,y:y_data})
                    term += 1
                if ep%100 == 0:
                    mse /= term
                    print(ep,"\tMSE:",mse)
                    term = 0
                    mse = 0
        rnn_params = sess.run(tf.trainable_variables('cells'))
        emg_params = sess.run(tf.trainable_variables('cell_emg'))
        dense1_params = sess.run(tf.trainable_variables('dense'))
        hidden_dense_params = sess.run(tf.trainable_variables('hidden_dense'))
        dense2_params = sess.run(tf.trainable_variables('dense2'))
        saver = tf.train.Saver()
        save_path = saver.save(sess, 'ckptset\\'+ saver_name);
        params_list = [rnn_params,emg_params,dense1_params,hidden_dense_params,dense2_params]
    return params_list
            
def KalmanFilter(Angle,Q_angle,Q_omega,R,Kalman_params = None):
    if(Kalman_params == None):
        P00 = Q_angle
        P01 = 0
        P10 = 0
        P11 = Q_omega
        omega = 0
        pre_angle = Angle
        angle = Angle
    else:
        pre_angle = Kalman_params[0]
        omega = Kalman_params[1]
        P00 = Kalman_params[2]
        P01 = Kalman_params[3]
        P10 = Kalman_params[4]
        P11 = Kalman_params[5]
        
        Theta_K = pre_angle + omega * 0.01
        
        P00 += (P10 + P01)*0.01 + Q_angle
        P10 += P11*0.01
        P01 += P11*0.01
        P11 += Q_omega
        
        K0 = P00/(R+P00)
        K1 = P10/(R+P00)
        
        angle = Theta_K + K0*(Angle - Theta_K)
        omega = omega + K1*(Angle - Theta_K)
        
    Kalman_params = [angle,omega,P00,P01,P10,P11]
    return Kalman_params;

def verify_divid_and_join(testx,testy,start,end,params_list,beta,printout = True,Q_angle = 0.5,Q_omega = 10,R = 0.5,alpha = 0.005):
    #params_list = [rnn_params,emg_params,dense1_params,hidden_dense_params,dense2_params]
    rnn_params = params_list[0]
    emg_params = params_list[1]
    dense1_params = params_list[2]
    hidden_dense_params = params_list[3]
    dense2_params = params_list[4]
    rnnW1 = rnn_params[0]
    rnnb1 = rnn_params[1].reshape(1,-1)
    rnnW2 = rnn_params[2]
    rnnb2 = rnn_params[3].reshape(1,-1)
    rnnW3 = rnn_params[4]
    rnnb3 = rnn_params[5].reshape(1,-1)
    
    emgW1 = emg_params[0]
    emgb1 = emg_params[1].reshape(1,-1)
    emgW2 = emg_params[2]
    emgb2 = emg_params[3].reshape(1,-1)
    
    denseW1 = dense1_params[0]
    denseb1 = dense1_params[1].reshape(1,-1)
    denseW2 = hidden_dense_params[0]
    denseb2 = hidden_dense_params[1].reshape(1,-1)
    denseW3 = dense2_params[0].copy()
    denseb3 = dense2_params[1].reshape(1,-1).copy()
    
    mean1 = -80 
    std1 = 15 
    meanw1 = 0
    stdw1 = 75

    mean2 = -110
    std2 = 15
    meanw2 = 0
    stdw2 = 90

    meany = 35
    stdy = 15

    input_angle_size = rnn_params[0].shape[0] - rnn_params[0].shape[1]
    input_emg_size = emg_params[0].shape[0] - emg_params[0].shape[1]

    hiddensize = rnnW1.shape[1]
    rnnsize2 = rnnW2.shape[1]
    rnnsize3 = rnnW3.shape[1]
    
    rnn_emg_size = emgW1.shape[1]
    
    hiddenlayersize = len(denseb1)
    rnn_state_size = len(rnnb1)
    outputsize = len(denseb3)
    Test_angle_input = np.zeros((1,input_angle_size+hiddensize))
    Test_emg_input = np.zeros((1,input_emg_size+rnn_emg_size))
    State1 = np.zeros((1,hiddensize))
    State2 = np.zeros((1,rnnsize2))
    State3 = np.zeros((1,rnnsize3))
    emgState1 = np.zeros((1,rnn_emg_size))
    emgState2 = np.zeros((1,rnn_emg_size))
    temp_input = np.zeros((1,hiddensize + rnnsize2));
    temp_input2 = np.zeros((1,2*rnn_emg_size));
    concate_input = np.zeros((1,rnnsize3 + rnn_emg_size))
    ####         FeedBack                ######
    
    Queue_hidden2 = np.zeros((5,15))
    ptr = 0;
    
    ####                                 #####
    finaloutput = np.zeros((testx.shape[0],outputsize))
    unnormal = np.zeros((testx.shape[0],outputsize))
    for i in range(testx.shape[0]):
        Test_angle_input[0,:input_angle_size] = testx[i,0:4].T
        Test_angle_input[0,input_angle_size:] = State1
        State1 = Test_angle_input.dot(rnnW1) + rnnb1
        State1[State1<0] = 0

        temp_input[0,0:hiddensize] = State1
        temp_input[0,hiddensize:] = State2
        State2 = temp_input.dot(rnnW2) + rnnb2
        State2[State2<0] = 0

        temp_input[0,0:rnnsize2] = State2
        temp_input[0,rnnsize2:] = State3
        State3 = temp_input.dot(rnnW3) + rnnb3
        State3[State3<0] = 0
        
        Test_emg_input[0,0:input_emg_size] = testx[i,4:7].T
        Test_emg_input[0,input_emg_size:] = emgState1
        emgState1 = Test_emg_input.dot(emgW1) + emgb1
        emgState1[emgState1<0] = 0
        
        temp_input2[0,0:rnn_emg_size] = emgState1
        temp_input2[0,rnn_emg_size:] = emgState2
        emgState2 = temp_input2.dot(emgW2) + emgb2
        emgState2[emgState2<0] = 0
        
        concate_input[0,0:hiddensize] = State3
        concate_input[0,hiddensize:] = emgState2
        
        hidden = concate_input.dot(denseW1)+denseb1 
        hidden[hidden<0] = 0

        hidden2 = hidden.dot(denseW2) + denseb2
        hidden2[hidden2<0] = 0

        tempoutput = hidden2.dot(denseW3) + denseb3
        
        if(i==0):
            temp_uno = tempoutput*15 + 35
            Kalman_params = KalmanFilter(temp_uno,Q_angle,Q_omega,R)
            finaloutput[i,:] = (Kalman_params[0]-35)/15
            
        elif(i<5):
            
            temp_uno = (tempoutput*15 + 35)*beta + (1-beta)*temp_uno
            Kalman_params = KalmanFilter(temp_uno,Q_angle,Q_omega,R,Kalman_params)
            finaloutput[i,:] = (Kalman_params[0]-35)/15
            
          ### Feedback here  #### 
        else:
            x_k5 = (testx[i,0]*std1+mean1-(testx[i,2]*std2 + mean2) - meany)/stdy
            y_k = finaloutput[i-5,:]
            diff = x_k5 - y_k
            denseW3 += alpha * (diff) * Queue_hidden2[ptr,:].reshape([15,1])
            denseb3 += alpha * diff
            
            temp_uno = (tempoutput*15 + 35)*beta + (1-beta)*temp_uno
            Kalman_params = KalmanFilter(temp_uno,Q_angle,Q_omega,R,Kalman_params)
            finaloutput[i,:] = (Kalman_params[0]-35)/15
            
            
        Queue_hidden2[ptr,:] = hidden2[0]
        ptr = (ptr+1)%5
        
    RNNmse = np.mean(np.square(finaloutput[start:end,:] - testy[start:end,:])*stdy**2)
    RNNmse2 = np.mean(np.square(finaloutput[start:end,:] - testy[start:end,:]))
    RNNqua = np.mean(np.square(np.square(finaloutput[start:end,:] - testy[start:end,:])))
    if(printout):

        #another naive method
        naivey = np.zeros(testy.shape)
        index = 1000
        naivemse2 = 1000;
        for i in range(200):
            naivey[:,0] = ((testx[:,0]*std1 + mean1 + (testx[:,1]*stdw1+meanw1)*0.001*(i-100))
                       - (testx[:,2]*std2 + mean2 + (testx[:,3]*stdw2+meanw2)*0.01*(i-100)))
            naivemse1 = np.mean(np.square(naivey[start:end,:] - testy[start:end,:]*stdy-meany))
            if(naivemse1<naivemse2):
                index = (i-100)/10
                naivemse2 = np.min((naivemse1,naivemse2))

        naivey[:,0] = ((testx[:,0]*std1 + mean1 + (testx[:,1]*stdw1+meanw1)*0.01*index)
                       - (testx[:,2]*std2 + mean2 + (testx[:,3]*stdw2+meanw2)*0.01*index))

        print("RNN mse:",RNNmse)
        print("RNN normalized mse",RNNmse2)
        print('Fourth order',RNNqua)
        print("naive mse:",np.min((naivemse1,naivemse2)))
        print('naive guess:',index)

        plt.figure(1,figsize = (18,1*5.4))
        plt.title("Angle diff Forecast vs Actual",fontsize = 14)

        plt.plot(pd.Series(testx[start:end,0]*std1+mean1 - testx[start:end,2]*std2-mean2),'y-',markersize = 1,label = 'Current Info')
        plt.plot(pd.Series(np.ravel(testy[start:end,0]*stdy+meany)),"b-",markersize = 1,label = 'Actual')
        plt.plot(pd.Series(np.ravel(finaloutput[start:end,0]*stdy+meany)),"r-",markersize = 1,label = 'Forecast')
        plt.plot(pd.Series(naivey[start:end,0]),'g-',markersize = 1,label = 'naive guess')
        plt.legend(loc = "upper left")
        plt.xlabel("Time Periods")

        plt.show()
    return [RNNmse2,RNNqua]

def total_verify(params_list,data_dict,filenum,setting = 'test',start = 1000,end = 50000,Q_angle = 0.004,Q_omega = 0.04,R = 2,alpha = 0.001):
    RNN_MSE = 0;
    RNN_QUA = 0;
    total_length = 0;
    for index in range(1,( (setting=='data') + 1)*filenum+1):
        testx = data_dict[setting + 'x' + str(index)][:,:]
        testy = data_dict[setting + 'y' + str(index)][:,:]
        mse =  verify_divid_and_join(testx,testy,start,end,params_list,1,False,Q_angle,Q_omega,R,alpha);
        length = data_dict[setting + 'x' + str(index)].shape[0]
        total_length += length
        RNN_MSE += mse[0]*length
        RNN_QUA += mse[1]*length
    if(setting == 'data'):
        print('On Training set')
    elif(setting == 'test'):
        print('On Test set:')
    print(RNN_MSE/total_length)
    print(RNN_QUA/total_length)
    return [RNN_MSE/total_length,RNN_QUA/total_length]

def writematrix(parameters,filename = 'parameters.txt'):
    
    with open(filename,'w') as f:
        f.write('{');
        for i in range(parameters.shape[0]):
            f.write('{');
            for j in range(parameters.shape[1]):
                if(j != parameters.shape[1]-1):
                    f.write("%.9ff,"%parameters[i][j])
                else:
                    f.write("%.9ff"%parameters[i][j])
            f.write('},')
            f.write('\n')
        f.write('};')
        f.write('\n')

def write_params_list(params_list):
    rnn_params = params_list[0]
    emg_params = params_list[1]
    dense1_params = params_list[2]
    hidden_dense_params = params_list[3]
    dense2_params = params_list[4]
    rnnW1 = rnn_params[0]
    rnnb1 = rnn_params[1].reshape(1,-1)
    rnnW2 = rnn_params[2]
    rnnb2 = rnn_params[3].reshape(1,-1)
    rnnW3 = rnn_params[4]
    rnnb3 = rnn_params[5].reshape(1,-1)
    
    emgW1 = emg_params[0]
    emgb1 = emg_params[1].reshape(1,-1)
    emgW2 = emg_params[2]
    emgb2 = emg_params[3].reshape(1,-1)
    
    denseW1 = dense1_params[0]
    denseb1 = dense1_params[1].reshape(1,-1)
    denseW2 = hidden_dense_params[0]
    denseb2 = hidden_dense_params[1].reshape(1,-1)
    denseW3 = dense2_params[0].copy()
    denseb3 = dense2_params[1].reshape(1,-1).copy()
    writematrix(rnnW1.T,'parameters_txt\\rnnW1.txt')
    writematrix(rnnb1,'parameters_txt\\rnnb1.txt')
    writematrix(rnnW2.T,'parameters_txt\\rnnW2.txt')
    writematrix(rnnb2,'parameters_txt\\rnnb2.txt')
    writematrix(rnnW3.T,'parameters_txt\\rnnW3.txt')
    writematrix(rnnb3,'parameters_txt\\rnnb3.txt')
    writematrix(denseW1.T,'parameters_txt\\denseW1.txt')
    writematrix(denseb1,'parameters_txt\\denseb1.txt')
    writematrix(denseW2.T,'parameters_txt\\denseW2.txt')
    writematrix(denseb2,'parameters_txt\\denseb2.txt')
    writematrix(denseW3.T,'parameters_txt\\denseW3.txt')
    writematrix(denseb3,'parameters_txt\\denseb3.txt')
    writematrix(emgW1.T,'parameters_txt\\emgW1.txt')
    writematrix(emgb1,'parameters_txt\\emgb1.txt')
    writematrix(emgW2.T,'parameters_txt\\emgW2.txt')
    writematrix(emgb2,'parameters_txt\\emgb2.txt')
