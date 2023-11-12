import PySimpleGUI as sg
import transcription
import communicateChatGPT
import os
import traceback

#初期値設定
openAiKey = ''
screenId = '' #画面ID(この値によって画面の動作を管理する)

#編集画面で使用
templateMsg = '次の文章から議事録を作成してください。また、日本語で回答してください。'
templateMsg2 = '次の文章を要約してください。また、日本語で回答してください。'
chunkSize = 1000 #チャンクサイズ(langChain)
searchResult = '' #単語検索の初期値
transcriptLength = '' #文字起こし結果の文字数


#----------------------画面の定義 開始----------------------
def make_init():
    # ------------ 初期画面 ------------
    main_layout = [
            [sg.Text("音声ファイルを選択してください。")],
            [sg.Text("(MP3,MP4,MPEG,MPGA,M4A,WAV,WebMに対応しています。)")],
            [sg.InputText(size=(60), key='-audioFilePath-'), sg.FileBrowse()],
            [sg.Text("OpenAiキーを入力してください。")],
            [sg.InputText(size=(60), password_char="*", key='-openAiKey-')],
            [sg.Button("文字起こしを実行")],
            [sg.Button("Exit")]]
    return sg.Window("初期画面", main_layout, finalize=True, size=(800, 600))

def make_setting():
    # ------------ 設定画面 ------------
    sub_layout = [
            [sg.Text("ChatGPTに送る文章を入力してください。")],
            [sg.InputText(default_text=templateMsg, size=(100), key='-templateMsg-')],
            [sg.Text("コンバインドメッセージを入力してください。")],
            [sg.InputText(default_text=templateMsg2, size=(100), key='-templateMsg2-')],
            [sg.Text("チャンクサイズを設定してください。")],
            [sg.InputText(default_text=chunkSize, size=(100), key='-chunkSize-')],
            [sg.Text("文字起こし内容から置き換えたい単語を入力してください。")],
            [sg.InputText(default_text='', size=(100), key='-replaceTarget-')],
            [sg.Text("置き換え後の単語を入力してください。(空なら削除になります。)")],
            [sg.InputText(default_text='', size=(100), key='-replaceResult-')],
            [sg.Button("文字列の置き換えを実行")],
            [sg.Text("文字起こし内容から検索したい単語を入力してください。")],
            [sg.InputText(default_text='', size=(100), key='-searchTarget-')],
            [sg.Text("文章内に上記の単語が存在する数を表示します。")],
            [sg.InputText(default_text=searchResult, size=(100), key='-searchResult-')],
            [sg.Button("文字列の検索を実行")],
            [sg.Text("文字起こし結果の文字数を表示します。")],
            [sg.InputText(default_text=transcriptLength, size=(100), key='-transcriptLength-')],
            [sg.Button("文字起こし画面に遷移")],
            [sg.Button("要約を実行")],
            [sg.Button("Exit")]]
    return sg.Window("設定画面", sub_layout, finalize=True, size=(800, 600))

def make_transcription():
    # ------------ 文字起こし画面 ------------
    sub_layout = [
            [sg.Multiline(default_text=transcript, size=(300, 28), key='-transcript-')],
            [sg.Button("設定画面に遷移")],
            [sg.Button("要約を実行")],
            [sg.Button("Exit")]]
    return sg.Window("文字起こし画面", sub_layout, finalize=True, size=(800, 600))

def make_result():
    # ------------ 要約結果画面 ------------
    sub_layout = [
            [sg.Multiline(default_text='要約結果', size=(300, 28), key='-resultScript-')],
            [sg.Button("設定画面に遷移")],
            [sg.Button("Exit")]]
    return sg.Window("要約結果画面", sub_layout, finalize=True, size=(800, 600))
#----------------------画面の定義 終了----------------------


screenId = "init" # 初期画面のIDをセット
window = make_init()# 初期画面を開く

while True:
    event, values = window.read()

    # Exitが押下された場合
    if event == sg.WIN_CLOSED or event == "Exit":
        break#画面を終了させる。

    #文字起こしを実行が押下された場合
    elif event == "文字起こしを実行":
        openAiKey = values['-openAiKey-']
        filePath = values['-audioFilePath-']

        #音声ファイルの選択確認
        if filePath == "":
            #エラーメッセージを設定する。
            sg.Popup("音声ファイルが選択されていません。", button_color=["#FFFFFF","#FF0000"])
            continue

        #OpenAiキーの入力確認
        if openAiKey == "":
            #エラーメッセージを設定する。
            sg.Popup("OpenAIキーが入力されていません。", button_color=["#FFFFFF","#FF0000"])
            continue

        #拡張子を取得
        root, ext = os.path.splitext(filePath)
        ext = ext.replace('.','')
        
        try:
            transcript = transcription.transcriptionAudio(values['-audioFilePath-'], ext, values['-openAiKey-'])
        except:
            print('例外発生')
            print('------------------------------')
            print('# traceback.format_exc()')
            t = traceback.format_exc()
            print(t)
            print('------------------------------')
            #エラーメッセージを設定する。
            sg.Popup("予期せぬエラーが発生しました。ファイルが対応していない可能性があります。", button_color=["#FFFFFF","#FF0000"])
            continue

        #文字起こしの文字数をセット
        transcriptLength = len(transcript)

        screenId = "setting"# 設定画面のIDをセット
        window.close()# 画面を閉じる
        window = make_setting()# 設定画面を開く

    
    
    # 文字列の置き換えを実行ボタンが押された場合
    elif event == "文字列の置き換えを実行":

        replaceTarget = values['-replaceTarget-']
        replaceResult = values['-replaceResult-']

        transcript = transcript.replace(replaceTarget, replaceResult)
        transcriptLength = len(transcript)
        window['-transcriptLength-'].update(value=transcriptLength)
    
    # 文字列の検索を実行ボタンが押された場合
    elif event == "文字列の検索を実行":
        searchTarget = values['-searchTarget-']
        searchResult = transcript.count(searchTarget)
        
        window['-searchResult-'].update(value=searchResult)

    # 文字起こし画面に遷移が押された場合
    elif event == "文字起こし画面に遷移":

        if screenId == "setting":
            templateMsg = values['-templateMsg-']
            templateMsg2 = values['-templateMsg2-']
            chunkSize = values['-chunkSize-']

        screenId = "transcription"# 文字起こし画面のIDをセット
        window.close()# 画面を閉じる
        window = make_transcription()# 文字起こし画面を開く
    
    # 設定画面に遷移が押下された場合
    elif event == "設定画面に遷移":

        if screenId == "transcription":
            transcript = values['-transcript-']
            transcriptLength = len(transcript)

        screenId = "setting"# 設定画面のIDをセット
        window.close()# 画面を閉じる
        window = make_setting()# 設定画面を開く

    # 要約を実行ボタンが押された場合
    elif event == "要約を実行":
        
        #遷移前画面が設定画面の場合
        if screenId == "setting":
            #print("setting画面から遷移した")
            templateMsg = values['-templateMsg-']
            templateMsg2 = values['-templateMsg2-']
            chunkSize = values['-chunkSize-']

        #遷移前画面が文字起こし画面の場合
        if screenId == "transcription":
            #print("文字起こし画面から遷移した")
            transcript = values['-transcript-']

        result = communicateChatGPT.communicate(transcript, openAiKey, templateMsg, templateMsg2, chunkSize)

        screenId = 'result'# 要約結果画面のIDをセット
        window.close()# 画面を閉じる
        window = make_result()# 要約結果画面を開く
        window['-resultScript-'].update(value=result)


# ウィンドウを終了する
window.close()