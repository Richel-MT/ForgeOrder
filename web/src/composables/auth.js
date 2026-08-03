import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request.js'
import { createLogger } from '@/utils/log.js'

export function useAuth() {
    

    const router = useRouter()

    const token = ref(localStorage.getItem('token') || '')
    const userInfo = ref(null)
    try{
        userInfo.value = JSON.parse(localStorage.getItem('userInfo') || 'null')
    }
    catch(error) {
            console.error(error)
            userInfo.value = null
        }
    
    const isLoggedIn = computed(() => token.value != '')

    const login = async(username, password, cover) => {
        const logger = createLogger('Auth.Login')
        try {
            const res = await request.post('/auth/login', {
                username,
                password,
                cover
            })
            

            if (res.status == 200) {
                if (res.data.status == 0 || res.data.status == 3003) {
                    // 登录成功
                    logger.info("登录成功")

                    token.value = res.data.data.token

                    userInfo.value = res.data.data.user

                    localStorage.setItem('token', token.value)
                    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))


                    router.push("/")

                    return res.data
                } else {
                    // else 登录失败，交给业务层处理
                    logger.error(`登录失败，${res.data.status}`)
                }
                
            }


            return res.data
            

        } catch (error) {
            logger.error("登录失败")
            logger.error(error)
            return {
                status: -1,
                data: error
            }
        }
    }

    const logout = async() => {
        const logger = createLogger('Auth.Logout')
        try {
            const res = await request.post('/auth/logout')
            if (res.status == 200 && res.data.status == 0) {
                // 退出登录成功
                logger.info("退出登录成功")
                token.value = ''
                userInfo.value = null
                localStorage.removeItem('token')
                localStorage.removeItem('userInfo')

                router.push('/login')
                
                return res.data
            } 
        } catch (error) {
            logger.error("退出登录失败")
            logger.error(error)
            return {
                status: -1,
                data: error
            }
        }   
    }
    
    return {
        login,
        logout,
        token,
        userInfo,
        isLoggedIn
    }
}