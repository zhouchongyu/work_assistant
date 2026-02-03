// frontend/src/stores/dict.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useDictStore = defineStore('dict', () => {
  // 字典数据，格式为 { [dictType]: { [dictValue]: dictLabel } }
  const dictData = ref<{ [key: string]: { [key: string]: string } }>({});

  // 加载字典数据
  const loadDict = async (dictType: string) => {
    // TODO: 实现字典加载逻辑
    // 这里应该调用后端API获取字典数据
    // 示例伪代码：
    // const response = await api.getDictByType(dictType);
    // dictData.value[dictType] = response.data.reduce((acc, item) => {
    //   acc[item.value] = item.label;
    //   return acc;
    // }, {});
  };

  // 获取字典标签
  const getDictLabel = (dictType: string, dictValue: string) => {
    return dictData.value[dictType]?.[dictValue] || dictValue;
  };

  // 获取字典选项列表
  const getDictOptions = (dictType: string) => {
    const typeData = dictData.value[dictType];
    if (!typeData) return [];
    
    return Object.entries(typeData).map(([value, label]) => ({
      value,
      label
    }));
  };

  // 初始化字典数据
  const initDicts = async (dictTypes: string[]) => {
    for (const type of dictTypes) {
      if (!dictData.value[type]) {
        await loadDict(type);
      }
    }
  };

  return {
    dictData,
    loadDict,
    getDictLabel,
    getDictOptions,
    initDicts
  };
});