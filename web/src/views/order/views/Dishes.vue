<template>
    <div>
        <div class="main-container" style="position: relative; height: calc(100vh - 64px); width:100vw">
            <div class="container mdui-prose" style="height: calc(100vh - 64px - 80px); overflow-y: hidden">
                <!-- <h2>选择菜品</h2> -->

                <div style="display: flex; height: calc(100%);">
                    <div style="min-width: 10%; max-width: 20%; flex-shrink: 0;">
                        <h4 style="text-align: center;">分类</h4>
                        <mdui-list v-for="(name, id) in categories" :key="id">
                            <mdui-list-item rounded @click="goToCategory(id)">{{name}}</mdui-list-item>
                        </mdui-list>
                    </div>

                    <div style="padding: 0 10px">
                        <mdui-divider vertical></mdui-divider>
                    </div>  

                    <div style="flex-grow: 1; overflow-y: auto; padding-right: 8px">
                        <div v-for="(name, id) in categories" :key="id" >
                            <div style="font-size: 20px" :ref="el => setCategoryRef(el, id)">{{name}}</div>
                            <mdui-divider style="margin-bottom: 16px"></mdui-divider>
                            


                            <div v-for="dish in dishes[name]" :key="dish.id" >
                                <!-- <div>{{ dish }}</div>
                                <div>{{ dish.category }} {{ id }}</div> -->
                                <div v-if="dish.category == id">
                                    <DishCard :dish="dish" :key="dish.id" @update="updateDish" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>

            <mdui-bottom-app-bar scroll-target=".main-container">
                <mdui-button style="height: 56px; border-radius: var(--mdui-shape-corner-large)" variant="tonal" @click="SelectedDishesDialog.open = true">
                    {{selectedDishes.length}}个菜品
                    <mdui-icon-shopping-cart slot="icon" style="width: 24px; height: 24px;"></mdui-icon-shopping-cart>
                </mdui-button>
                <div style="flex-grow: 1"></div>

                <mdui-fab style="height: 56px; border-radius: var(--mdui-shape-corner-large)" @click="prevStep">
                    <mdui-icon-arrow-back slot="icon" style="width: 24px; height: 24px;"></mdui-icon-arrow-back>
                </mdui-fab>

                <mdui-button 
                    @click="nextStep" 
                    style="height: 56px; border-radius: var(--mdui-shape-corner-large)"
                    :disabled="selectedDishes.length == 0"
                    >
                    选好了
                    <mdui-icon-arrow-forward slot="icon" style="width: 24px; height: 24px;"></mdui-icon-arrow-forward>
                </mdui-button>
            </mdui-bottom-app-bar>

        </div>

        <mdui-dialog 
            headline="购物车"
            ref="SelectedDishesDialog"
            close-on-esc
            close-on-overlay-click
            class="shopping-card-dialog"    
        >
                <div v-if="selectedDishes.length > 0" style="overflow: auto;">
                    <mdui-list >
                        <mdui-list-item v-for="dish in selectedDishes" :key="dish.id" rounded>
                            {{ dish.dishInfo.name }}
                            <div style="font-size: 16px; line-height: 1;">
                                x{{ dish.count }},
                                <span v-for="(choice, index) in dish.choices" :key="index">{{choice}}</span> 
                            </div>
                        </mdui-list-item>
                    </mdui-list>
                </div>

                <div v-else style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: calc(50vh - 32px - 64px);">
                    <mdui-icon-remove-shopping-cart style="width: 48px; height: 48px; margin-bottom: 20px"></mdui-icon-remove-shopping-cart>
                    <div style="font-size: 20px; line-height: 1;">暂无菜品</div>
                </div>
                
        </mdui-dialog>
    </div>
</template>

<script setup> 
    import 'mdui/components/list.js'
    import 'mdui/components/list-item.js'
    import 'mdui/components/radio-group.js'
    import 'mdui/components/radio.js'
    import 'mdui/components/bottom-app-bar.js'
    import 'mdui/components/divider.js'
    import 'mdui/components/dialog.js'

    import '@mdui/icons/error.js'
    import '@mdui/icons/arrow-forward.js'
    import '@mdui/icons/shopping-cart.js'
    import '@mdui/icons/remove-shopping-cart.js';

    import DishCard from '../components/DishCard.vue'
    
    import { ref, onMounted, watch } from 'vue'
    import request from '@/utils/request.js'
    
    const props = defineProps(['index', 'dishInfo'])
    const emit = defineEmits(['update:index', 'update:dishInfo'])

    const SelectedDishesDialog = ref(null)
    const categoryRefs = ref({})

    const categories = ref({})
    const dishes = ref({})

    const selectedDishes = ref([])

    const getDishes = async () => {
        try {
            const res = await request.get('/shop/dishes/getAll')
            if (res.data.status == 0) {
                dishes.value = res.data.data.dishes
                categories.value = res.data.data.categories
            }
        } catch (error) {
            console.error(error)
            dishes.value = []
        } 
    }

    const updateDish = (newVal) => {
        const item = selectedDishes.value.find((item) => item.id == newVal.id && JSON.stringify(item.choices) == JSON.stringify(newVal.choices))
        
        // console.log(item)
        if (item) {
            const index = selectedDishes.value.indexOf(item)
            selectedDishes.value[index].count += newVal.count

        } else {
            selectedDishes.value.push(newVal)
        }
    }

    const setCategoryRef = (el, id) => {
        if (el) {
            categoryRefs.value[id] = el
        }
    }

    const goToCategory = (id) => {
        const target = categoryRefs.value[id]
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
                inline: 'nearest'
            })
        }
    }

    onMounted(() => {
        getDishes()
    })

    const nextStep = () => {
        emit('update:index', props.index + 1)
        emit('update:dishInfo', {
            "dishes": selectedDishes.value
        })
    }

    const prevStep = () => {
        emit('update:index', props.index - 1)
    }

    // watch(selectedDishes.value, (newVal, oldVal) => {
    //     // console.log(JSON.stringify(newVal))
    // })


</script>

<style>
    .loading-tables {
        display: flex;
        flex-direction: column;
        gap: 20px;
        justify-content: center;
        align-items: center;
        height: 20vh;  
    }

    mdui-dialog.shopping-card-dialog::part(panel) {
        min-width: 100vw;
        max-width: 100vw;
        height: 50vh;
        position: fixed;
        bottom: 0;
        border-radius: var(--mdui-shape-corner-large) var(--mdui-shape-corner-large) 0 0 ;
    }
</style>