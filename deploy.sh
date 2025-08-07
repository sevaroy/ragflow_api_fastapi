#!/bin/bash

# =============================================================================
# RAGFlow + RAGAS 智能評估平台 - 本地部署腳本
# =============================================================================
# 
# 功能說明：
# 1. 自動檢查和安裝依賴
# 2. 設置虛擬環境
# 3. 配置環境變數
# 4. 啟動 Streamlit 應用
# 5. 提供健康檢查和故障排除
#
# 使用方式：
#   chmod +x deploy.sh
#   ./deploy.sh
# =============================================================================

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 項目信息
PROJECT_NAME="RAGFlow + RAGAS 智能評估平台"
PROJECT_DIR=$(pwd)
VENV_DIR="venv"
STREAMLIT_PORT=8501
LOG_FILE="deployment.log"

# 打印帶顏色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo -e "${PURPLE}"
    echo "==============================================================================="
    echo "🚀 $1"
    echo "==============================================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 記錄日志
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 檢查命令是否存在
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 檢查系統需求
check_system_requirements() {
    print_step "檢查系統需求..."
    
    # 檢查 Python 版本
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        print_success "Python 3 已安裝: $(python3 --version)"
        log_message "Python version: $(python3 --version)"
        
        # 檢查是否為 Python 3.8+
        if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
            print_success "Python 版本符合需求 (3.8+)"
        else
            print_warning "建議使用 Python 3.8 或更高版本"
        fi
    else
        print_error "Python 3 未安裝，請先安裝 Python 3.8+"
        echo "安裝指南："
        echo "  macOS: brew install python@3.11"
        echo "  Ubuntu: sudo apt install python3 python3-pip python3-venv"
        echo "  CentOS: sudo yum install python3 python3-pip"
        exit 1
    fi
    
    # 檢查 pip
    if check_command pip3; then
        print_success "pip3 已安裝"
    else
        print_error "pip3 未安裝，請先安裝 pip3"
        exit 1
    fi
    
    # 檢查 git（可選）
    if check_command git; then
        print_success "Git 已安裝: $(git --version)"
    else
        print_warning "Git 未安裝，某些功能可能受限"
    fi
    
    # 檢查磁盤空間
    AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ "$AVAILABLE_SPACE" -gt 2 ]]; then
        print_success "磁盤空間充足: ${AVAILABLE_SPACE}GB 可用"
    else
        print_warning "磁盤空間較少: ${AVAILABLE_SPACE}GB 可用，建議至少有 2GB 空間"
    fi
}

# 設置虛擬環境
setup_virtual_environment() {
    print_step "設置 Python 虛擬環境..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "虛擬環境已存在，將重新創建..."
        rm -rf "$VENV_DIR"
        log_message "Removed existing virtual environment"
    fi
    
    # 創建虛擬環境
    print_message "$CYAN" "創建虛擬環境..."
    python3 -m venv "$VENV_DIR"
    
    # 激活虛擬環境
    print_message "$CYAN" "激活虛擬環境..."
    source "$VENV_DIR/bin/activate"
    
    # 升級 pip
    print_message "$CYAN" "升級 pip..."
    pip install --upgrade pip
    
    print_success "虛擬環境設置完成"
    log_message "Virtual environment created and activated"
}

# 安裝依賴
install_dependencies() {
    print_step "安裝項目依賴..."
    
    # 檢查 requirements.txt 是否存在
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt 文件未找到"
        print_message "$YELLOW" "正在創建基本的 requirements.txt..."
        cat > requirements.txt << EOF
streamlit>=1.28.0
streamlit-chat>=0.1.1
plotly>=5.17.0
pandas>=1.5.0
numpy>=1.24.0
requests>=2.28.0
python-dotenv>=1.0.0
ragas>=0.1.0
datasets>=2.14.0
openai>=1.0.0
watchdog>=3.0.0
EOF
        print_success "requirements.txt 已創建"
    fi
    
    # 安裝依賴
    print_message "$CYAN" "正在安裝 Python 依賴包..."
    pip install -r requirements.txt
    
    print_success "依賴安裝完成"
    log_message "Dependencies installed successfully"
    
    # 顯示已安裝的關鍵包
    print_message "$CYAN" "已安裝的關鍵包版本："
    pip show streamlit ragas plotly pandas | grep -E "Name|Version" | paste - -
}

# 配置環境變數
setup_environment() {
    print_step "配置環境變數..."
    
    if [ ! -f ".env" ]; then
        print_message "$CYAN" "創建環境變數配置文件..."
        cat > .env << EOF
# RAGFlow API 配置
RAGFLOW_API_URL=http://192.168.50.123:9380
RAGFLOW_API_KEY=your-ragflow-api-key-here

# OpenAI API 配置 (用於 RAGAS 評估)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# 其他設置
DEBUG=False
LOG_LEVEL=INFO

# Streamlit 配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
EOF
        print_success ".env 文件已創建"
        print_warning "請編輯 .env 文件，填入您的 API 金鑰"
        print_message "$YELLOW" "重要：需要配置以下項目："
        echo "  1. RAGFLOW_API_URL - RAGFlow 服務器地址"
        echo "  2. RAGFLOW_API_KEY - RAGFlow API 金鑰"
        echo "  3. OPENAI_API_KEY - OpenAI API 金鑰（用於 RAGAS 評估）"
        
        # 詢問是否現在配置
        read -p "是否現在配置環境變數？(y/N): " configure_now
        if [[ "$configure_now" =~ ^[Yy]$ ]]; then
            configure_environment_interactive
        fi
    else
        print_success ".env 文件已存在"
        log_message ".env file already exists"
    fi
}

# 交互式環境配置
configure_environment_interactive() {
    print_message "$CYAN" "開始交互式環境配置..."
    
    # RAGFlow API URL
    read -p "請輸入 RAGFlow API URL (默認: http://192.168.50.123:9380): " ragflow_url
    ragflow_url=${ragflow_url:-http://192.168.50.123:9380}
    
    # RAGFlow API Key
    read -p "請輸入 RAGFlow API Key: " ragflow_key
    
    # OpenAI API Key
    read -p "請輸入 OpenAI API Key (用於 RAGAS 評估): " openai_key
    
    # 更新 .env 文件
    sed -i.bak "s|RAGFLOW_API_URL=.*|RAGFLOW_API_URL=$ragflow_url|" .env
    sed -i.bak "s|RAGFLOW_API_KEY=.*|RAGFLOW_API_KEY=$ragflow_key|" .env
    sed -i.bak "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$openai_key|" .env
    
    rm .env.bak
    print_success "環境變數配置完成"
}

# 創建必要的目錄
create_directories() {
    print_step "創建必要的目錄結構..."
    
    directories=(
        "data"
        "data/conversations"
        "data/evaluations"
        "logs"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "創建目錄: $dir"
        fi
    done
    
    # 創建默認設置文件
    if [ ! -f "data/settings.json" ]; then
        cat > data/settings.json << EOF
{
    "app_name": "RAGFlow + RAGAS 智能評估平台",
    "version": "1.0.0",
    "default_settings": {
        "evaluation_threshold": 0.7,
        "max_test_cases": 50,
        "default_metrics": [
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "context_recall"
        ]
    },
    "ui_settings": {
        "theme": "dark",
        "show_debug": false
    }
}
EOF
        print_success "創建默認設置文件"
    fi
}

# 健康檢查
health_check() {
    print_step "執行健康檢查..."
    
    # 檢查虛擬環境
    if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
        print_success "虛擬環境正常"
    else
        print_error "虛擬環境異常"
        return 1
    fi
    
    # 檢查主要依賴
    source "$VENV_DIR/bin/activate"
    
    dependencies_to_check=(
        "streamlit"
        "pandas"
        "plotly"
        "requests"
    )
    
    for dep in "${dependencies_to_check[@]}"; do
        if python -c "import $dep" 2>/dev/null; then
            print_success "依賴檢查通過: $dep"
        else
            print_error "依賴檢查失敗: $dep"
            return 1
        fi
    done
    
    # 檢查主要文件
    main_files=(
        "integrated_ragflow_platform.py"
        "pages/chat.py"
        "pages/evaluation.py"
        "pages/dashboard.py"
        "ragflow_chatbot.py"
    )
    
    for file in "${main_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "文件檢查通過: $file"
        else
            print_warning "文件不存在: $file"
        fi
    done
    
    print_success "健康檢查完成"
}

# 啟動應用
start_application() {
    print_step "啟動 Streamlit 應用..."
    
    # 激活虛擬環境
    source "$VENV_DIR/bin/activate"
    
    # 檢查端口是否被占用
    if lsof -Pi :$STREAMLIT_PORT -sTCP:LISTEN -t >/dev/null; then
        print_warning "端口 $STREAMLIT_PORT 已被占用"
        read -p "是否終止占用進程並繼續？(y/N): " kill_process
        if [[ "$kill_process" =~ ^[Yy]$ ]]; then
            lsof -ti:$STREAMLIT_PORT | xargs kill -9
            print_success "已終止占用進程"
        else
            print_error "部署取消"
            exit 1
        fi
    fi
    
    print_message "$GREEN" "🚀 啟動 RAGFlow + RAGAS 智能評估平台..."
    print_message "$CYAN" "訪問地址: http://localhost:$STREAMLIT_PORT"
    print_message "$CYAN" "按 Ctrl+C 停止應用"
    
    log_message "Application started on port $STREAMLIT_PORT"
    
    # 啟動 Streamlit
    streamlit run integrated_ragflow_platform.py \
        --server.port=$STREAMLIT_PORT \
        --server.address=localhost \
        --server.headless=false \
        --browser.gatherUsageStats=false
}

# 顯示幫助信息
show_help() {
    print_header "RAGFlow + RAGAS 智能評估平台 - 部署腳本幫助"
    echo
    echo "使用方式："
    echo "  ./deploy.sh [選項]"
    echo
    echo "選項："
    echo "  -h, --help          顯示此幫助信息"
    echo "  -c, --check-only    僅執行系統檢查，不進行部署"
    echo "  -s, --setup-only    僅執行環境設置，不啟動應用"
    echo "  -q, --quick         快速部署（跳過交互式配置）"
    echo "  --port PORT         指定 Streamlit 端口（默認：8501）"
    echo "  --clean             清理所有生成的文件和虛擬環境"
    echo
    echo "示例："
    echo "  ./deploy.sh                    # 完整部署流程"
    echo "  ./deploy.sh -c                 # 僅檢查系統需求"
    echo "  ./deploy.sh -s                 # 僅設置環境，不啟動"
    echo "  ./deploy.sh --port 8080        # 使用自定義端口"
    echo "  ./deploy.sh --clean            # 清理環境"
    echo
}

# 清理環境
clean_environment() {
    print_header "清理環境"
    
    print_warning "這將刪除以下內容："
    echo "  - 虛擬環境目錄 ($VENV_DIR)"
    echo "  - 日志文件 ($LOG_FILE)"
    echo "  - 臨時文件和緩存"
    echo
    
    read -p "確定要清理環境？(y/N): " confirm_clean
    if [[ ! "$confirm_clean" =~ ^[Yy]$ ]]; then
        print_message "$CYAN" "清理操作已取消"
        exit 0
    fi
    
    print_step "清理虛擬環境..."
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
        print_success "虛擬環境已刪除"
    fi
    
    print_step "清理日志和臨時文件..."
    rm -f "$LOG_FILE"
    rm -rf __pycache__/
    rm -rf .pytest_cache/
    find . -name "*.pyc" -delete
    find . -name ".DS_Store" -delete
    
    print_success "環境清理完成"
}

# 主函數
main() {
    # 解析命令行參數
    CHECK_ONLY=false
    SETUP_ONLY=false
    QUICK_DEPLOY=false
    CLEAN_ENV=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--check-only)
                CHECK_ONLY=true
                shift
                ;;
            -s|--setup-only)
                SETUP_ONLY=true
                shift
                ;;
            -q|--quick)
                QUICK_DEPLOY=true
                shift
                ;;
            --port)
                STREAMLIT_PORT="$2"
                shift 2
                ;;
            --clean)
                CLEAN_ENV=true
                shift
                ;;
            *)
                print_error "未知選項: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 清理環境
    if [ "$CLEAN_ENV" = true ]; then
        clean_environment
        exit 0
    fi
    
    # 開始部署流程
    print_header "$PROJECT_NAME - 本地部署"
    print_message "$WHITE" "部署目錄: $PROJECT_DIR"
    print_message "$WHITE" "部署時間: $(date)"
    echo
    
    # 創建日志文件
    echo "# RAGFlow + RAGAS 部署日志" > "$LOG_FILE"
    log_message "Deployment started"
    
    # 執行部署步驟
    check_system_requirements
    
    if [ "$CHECK_ONLY" = true ]; then
        print_success "系統檢查完成"
        exit 0
    fi
    
    setup_virtual_environment
    install_dependencies
    
    if [ "$QUICK_DEPLOY" = false ]; then
        setup_environment
    else
        print_warning "快速部署模式：跳過環境配置"
    fi
    
    create_directories
    health_check
    
    if [ "$SETUP_ONLY" = true ]; then
        print_success "環境設置完成"
        print_message "$CYAN" "要啟動應用，請運行："
        print_message "$CYAN" "  source $VENV_DIR/bin/activate"
        print_message "$CYAN" "  streamlit run integrated_ragflow_platform.py"
        exit 0
    fi
    
    # 最終提示
    print_message "$GREEN" "🎉 部署準備完成！"
    echo
    print_message "$CYAN" "接下來將啟動應用，請確保："
    print_message "$CYAN" "1. RAGFlow 服務正在運行"
    print_message "$CYAN" "2. .env 文件中的 API 密鑰已正確配置"
    print_message "$CYAN" "3. 網絡連接正常"
    echo
    
    read -p "按 Enter 鍵啟動應用，或 Ctrl+C 取消..."
    
    start_application
}

# 處理中斷信號
trap 'print_message "$RED" "\n\n💥 部署中斷"; exit 1' INT TERM

# 執行主函數
main "$@"