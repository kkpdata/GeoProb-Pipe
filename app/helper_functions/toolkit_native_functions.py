"""
This script is native to the Probabilistic Toolkit, but with some minor changes.
Changes can be found by searching for "## changed""

The original script is placed on your machine when installing the Toolkit:
C:\\Program Files (x86)\\Deltares\\Probabilistic Toolkit\\bin\\Python\\toolkit.py

This script has only been tested in combination with version 2023.2.343.0 of the Probabilistic Toolkit
"""

import os
import socket
import sys
import time

SERVER_PORT = 11178  ## changed


def _SendMessage(message, waitForAnswer):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            if not "SERVER_PORT" in globals():
                SetPort(SERVER_PORT)  ## changed

            ip_address = socket.gethostbyname(socket.gethostname())
            s.connect((ip_address, SERVER_PORT))
            sent = s.send(message.encode())
            if waitForAnswer:
                data = s.recv(8192).decode()
                s.close()
                _CheckException(data)
                return data
            else:
                dummy_data = s.recv(256).decode()
                s.close()
                _CheckException(dummy_data)
                return ""
        except:
            message = sys.exc_info()[0]
            print("error: " + message, flush=True)
            s.close()
            raise


def _CheckException(data):
    exc_key = "exception:"
    if data.startswith(exc_key):
        raise ValueError(data[len(exc_key) : -1])


def SetPort(portnumber):
    try:
        global SERVER_PORT
        SERVER_PORT = portnumber
    except:
        print("error: setting port", flush=True)
        message = sys.exc_info()[0]
        print("error: " + message, flush=True)
        raise


def SuppressServer():
    try:
        global suppress_server
        suppress_server = True
    except:
        print("error: suppress server", flush=True)
        message = sys.exc_info()[0]
        print("error: " + message, flush=True)
        raise


def Initialize(PATH_TO_PTK_SERVER):
    ## changed
    if not "suppress_server" in globals():

        connected = False
        count = 0
        while not connected and count < 1:
            os.startfile(PATH_TO_PTK_SERVER)
            time.sleep(1)

            connected = CheckConnection()
            if not connected:
                time.sleep(1)
                count = count + 1


def CheckConnection():
    try:
        message = "Poll"
        data = _SendMessage(message, True)
        return True
    except:
        return False


def Exit():
    if not "suppress_server" in globals():
        message = "Exit"
        data = _SendMessage(message, False)


def Load(fileName):
    message = "Load:" + os.path.abspath(fileName)
    data = _SendMessage(message, False)


def Save(fileName):
    message = "Save:" + os.path.abspath(fileName)
    _SendMessage(message, False)


def GetIdentifier():
    message = "GetIdentifier"
    data = _SendMessage(message, True)
    return data


def SetIdentifier(identifier):
    message = "SetIdentifier:" + identifier
    _SendMessage(message, False)


def GetModelInputFile():
    message = "GetModelInputFileName"
    data = _SendMessage(message, True)
    return data


def SetModelInputFile(fileName):
    message = "SetModelInputFileName:" + os.path.abspath(fileName)
    _SendMessage(message, False)


def GetModelScriptFile():
    message = "GetModelScriptFileName"
    data = _SendMessage(message, True)
    return data


def SetModelScriptFile(fileName):
    message = "SetModelScriptFileName:" + os.path.abspath(fileName)
    _SendMessage(message, False)


def GetModelMethod():
    message = "GetModelMethodName"
    data = _SendMessage(message, True)
    return data


def SetModelMethod(methodName):
    message = "SetModelMethodName:" + methodName
    _SendMessage(message, False)


def GetSubModelInputFile(subModel):
    message = "GetSubModelInputFileName:" + subModel
    data = _SendMessage(message, True)
    return data


def SetSubModelInputFile(subModel, fileName):
    message = "SetSubModelInputFileName:" + subModel + ":" + os.path.abspath(fileName)
    _SendMessage(message, False)


def GetSubModelScriptFile(subModel):
    message = "GetSubModelScriptFileName:" + subModel
    data = _SendMessage(message, True)
    return data


def SetSubModelScriptFile(subModel, fileName):
    message = "SetSubModelScriptFileName:" + subModel + os.path.abspath(fileName)
    _SendMessage(message, False)


def GetSubModelMethod(subModel):
    message = "GetSubModelMethodName:" + subModel
    data = _SendMessage(message, True)
    return data


def SetSubModelMethod(subModel, methodName):
    message = "SetSubModelMethodName:" + subModel + methodName
    _SendMessage(message, False)


def GetSubModels():
    message = "GetSubModels"
    data = _SendMessage(message, True)
    return data.split(";")


def GetVariables():
    message = "GetVariables"
    data = _SendMessage(message, True)
    return data.split(";")


def GetResponseVariables():
    message = "GetResponseVariables"
    data = _SendMessage(message, True)
    return data.split(";")


def GetVariableQuantile(variable, quantile):
    message = "GetVariableQuantile:" + variable + ":" + str(quantile)
    data = _SendMessage(message, True)
    return float(data)


def GetVariableDistribution(variable):
    message = "GetVariableDistribution:" + variable
    data = _SendMessage(message, True)
    return data


def SetVariableDistribution(variable, distribution):
    message = "SetVariableDistribution:" + variable + ":" + distribution
    _SendMessage(message, False)


def GetVariableValue(variable, property):
    message = "GetVariableValue:" + variable + ":" + property
    data = _SendMessage(message, True)
    return float(data)


def GetVariableDesignFraction(variable):
    message = "GetVariableDesignFraction:" + variable
    data = _SendMessage(message, True)
    return float(data)


def GetVariableDesignFactor(variable):
    message = "GetVariableDesignFactor:" + variable
    data = _SendMessage(message, True)
    return float(data)


def GetVariableDesignValue(variable):
    message = "GetVariableDesignValue:" + variable
    data = _SendMessage(message, True)
    return float(data)


def ClearVariable(variable):
    message = "ClearVariable:" + variable
    _SendMessage(message, False)


def SetVariableValue(variable, property, value):
    message = "SetVariableValue:" + variable + ":" + property + ":" + str(value)
    _SendMessage(message, False)


def SetVariableDesignFraction(variable, value):
    message = "SetVariableDesignFraction:" + variable + ":" + str(value)
    _SendMessage(message, False)


def SetVariableDesignFactor(variable, value):
    message = "SetVariableDesignFactor:" + variable + ":" + str(value)
    _SendMessage(message, False)


def SetVariableDesignValue(variable, value):
    message = "SetVariableDesignValue:" + variable + ":" + str(value)
    _SendMessage(message, False)


def SetVariableFragilityValue(variable, type, x, reliability):
    message = "SetVariableFragilityValue:" + variable + ":" + type + ":" + str(x) + ":" + str(reliability)
    _SendMessage(message, False)


def SetVariableDiscreteValue(variable, x, amount):
    message = "SetVariableDiscreteValue:" + variable + ":" + str(x) + ":" + str(amount)
    _SendMessage(message, False)


def SetVariableTableValue(variable, lower, upper, amount):
    message = "SetVariableTableValue:" + variable + ":" + str(lower) + ":" + +str(upper) + ":" + str(amount)
    _SendMessage(message, False)


def GetCorrelation(var1, var2):
    message = "GetCorrelation:" + var1 + ":" + var2
    data = _SendMessage(message, True)
    return float(data)


def SetCorrelation(var1, var2, correlation):
    message = "SetCorrelation:" + var1 + ":" + var2 + ":" + str(correlation)
    _SendMessage(message, False)


def GetFragilityValues(values):
    message = "GetFragilityValues"
    data = _SendMessage(message, True)
    return list(map(float, data.split(";")))


def SetFragilityValues(values):
    message = "SetFragilityValues:" + ";".join(map(str, values))
    _SendMessage(message, False)


def GetSettingValue(property):
    message = "GetSettingValue:" + property
    data = _SendMessage(message, True)
    return float(data)


def SetSettingValue(property, value):
    message = "SetSettingValue:" + property + ":" + str(value)
    _SendMessage(message, False)


def GetSettingMethod():
    message = "GetSettingMethod"
    data = _SendMessage(message, True)
    return data


def SetSettingMethod(value):
    message = "SetSettingMethod:" + value
    _SendMessage(message, False)


def GetSettingStartMethod():
    message = "GetSettingStartMethod"
    data = _SendMessage(message, True)
    return data


def SetSettingStartMethod(value):
    message = "SetSettingStartMethod:" + value
    _SendMessage(message, False)


def GetStartValue(var1):
    message = "GetStartValue:" + var1
    data = _SendMessage(message, True)
    return float(data)


def SetStartValue(var1, startValue):
    message = "SetStartValue:" + var1 + ":" + str(startValue)
    _SendMessage(message, False)


def Validate():
    message = "Validate"
    return _SendMessage(message, True)


def Run():
    message = "Run"
    return _SendMessage(message, True)


def RunEmpty():
    message = "RunEmpty"
    return _SendMessage(message, False)


def RunSubModelEmpty(subModel):
    message = "RunSubModelEmpty:" + subModel
    return _SendMessage(message, False)


def GetUncertaintyStochasts():
    message = "GetUncertaintyStochasts"
    data = _SendMessage(message, True)
    return int(data)


def GetUncertaintyStochastName(index):
    message = "GetUncertaintyStochastName:" + str(index)
    data = _SendMessage(message, True)
    return data


def GetUncertaintyStochastQuantile(index, quantile):
    message = "GetUncertaintyStochastQuantile:" + str(index) + ":" + str(quantile)
    data = _SendMessage(message, True)
    return float(data)


def GetDesignPoints():
    message = "GetDesignPoints"
    data = _SendMessage(message, True)
    return int(data)


def GetNumericIdentifiers(design_point_index=0):
    message = "GetNumericIdentifiers:" + str(design_point_index)
    data = _SendMessage(message, True)
    return list(map(float, data.split(";")))


def GetReliabilityIndex(design_point_index=0):
    message = "GetReliabilityIndex:" + str(design_point_index)
    data = _SendMessage(message, True)
    return float(data)


def GetConvergence(design_point_index=0):
    message = "GetConvergence:" + str(design_point_index)
    data = _SendMessage(message, True)
    return float(data)


def GetProbabilityFailure(design_point_index=0):
    message = "GetProbabilityFailure:" + str(design_point_index)
    data = _SendMessage(message, True)
    return float(data)


def GetAlpha(variable, design_point_index=0):
    message = "GetAlpha:" + str(design_point_index) + ":" + variable
    data = _SendMessage(message, True)
    return float(data)


def GetAlphaPhysical(variable, design_point_index=0):
    message = "GetAlphaPhysical:" + str(design_point_index) + ":" + variable
    data = _SendMessage(message, True)
    return float(data)


def GetRealizations(design_point_index=0):
    message = "GetRealizations:" + str(design_point_index)
    data = _SendMessage(message, True)
    return int(data)


def GetRealizationValue(realization_index, variable, design_point_index=0):
    message = "GetRealizationValue:" + str(design_point_index) + ":" + str(realization_index) + ":" + variable
    data = _SendMessage(message, True)
    return float(data)


def GetRealizationProperty(realization_index, variable, design_point_index=0):
    message = "GetRealizationProperty:" + str(design_point_index) + ":" + str(realization_index) + ":" + variable
    data = _SendMessage(message, True)
    return float(data)
